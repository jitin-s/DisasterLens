"""
DisasterLens Decision Explainability (XAI) Engine
Computes exact Shapley feature attributions (TreeSHAP or Analytical Shapley Decomposition)
and synthesizes automated incident commander briefing notes.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from models.train_severity import FEATURE_COLUMNS, FastSeverityModel

FEATURE_HUMAN_NAMES = {
    "rainfall_mm_h": "Torrential Rainfall Intensity",
    "wind_gust_kmh": "Peak Wind Gust Velocity",
    "elevation_m": "Ground Elevation Profile",
    "drainage_capacity": "Drainage / Bayou Channel Capacity",
    "flood_gauge_m": "Flood Water Inundation Depth",
    "population_density": "Population Density per km²",
    "road_connectivity_pct": "Road Network Transit Connectivity",
    "power_grid_status_pct": "Electrical Grid Power Status",
    "elderly_ratio": "Elderly Population Concentration (≥65)",
    "pediatric_ratio": "Pediatric Dependent Ratio (<5)",
    "mobility_impaired_ratio": "Mobility-Impaired Demographic Ratio",
    "poverty_ratio": "Economic Deprivation / Poverty Index"
}


class DisasterExplainer:
    def __init__(self, model):
        self.model = model
        self.tree_explainer = None
        
        # Check if model has shap TreeExplainer support
        if not isinstance(model, FastSeverityModel):
            try:
                import shap
                self.tree_explainer = shap.TreeExplainer(model)
            except Exception:
                self.tree_explainer = None

    def explain_zones(self, df: pd.DataFrame) -> Tuple[np.ndarray, float]:
        """
        Computes SHAP values for all operational zones.
        Returns:
            shap_values: np.ndarray of shape (n_zones, n_features)
            base_value: float expected value of model
        """
        X = df[FEATURE_COLUMNS]
        
        if self.tree_explainer is not None:
            explanation = self.tree_explainer(X)
            return explanation.values, float(self.tree_explainer.expected_value)
            
        # Analytical Shapley computation for FastSeverityModel:
        # phi_j(x) = w_j * (x_j - mu_j) / sigma_j
        X_vals = X.values
        if hasattr(self.model, "weights") and hasattr(self.model, "mean"):
            X_norm = (X_vals - self.model.mean) / self.model.std
            shap_values = X_norm * self.model.weights
            base_value = float(self.model.intercept)
        else:
            shap_values = np.zeros(X_vals.shape)
            base_value = 0.5
            
        return shap_values, base_value

    def get_zone_attribution(
        self,
        zone_row: pd.Series,
        zone_shap: np.ndarray,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Decomposes a single zone's prediction into top risk drivers and percentage influence.
        """
        drivers = []
        abs_sum = np.sum(np.abs(zone_shap)) + 1e-6
        
        for idx, feat in enumerate(FEATURE_COLUMNS):
            val = float(zone_row.get(feat, 0.0))
            sh_val = float(zone_shap[idx])
            drivers.append({
                "feature": feat,
                "label": FEATURE_HUMAN_NAMES.get(feat, feat),
                "actual_value": val,
                "shap_value": round(sh_val, 4),
                "abs_impact_pct": round(abs(sh_val) / abs_sum * 100.0, 1),
                "direction": "Increases Risk" if sh_val > 0 else "Decreases Risk"
            })
            
        # Sort descending by absolute impact
        drivers.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        top_drivers = drivers[:top_k]
        
        # Build Natural Language Incident Commander Briefing Note
        zone_id = zone_row.get("zone_id", "Zone")
        zone_name = zone_row.get("zone_name", zone_id)
        opi = float(zone_row.get("opi_score", 0.0))
        tier = zone_row.get("triage_tier", "Unspecified")
        
        # Identify top positive contributors (driving up severity)
        pos_drivers = [d for d in drivers if d["shap_value"] > 0]
        if pos_drivers:
            d1 = pos_drivers[0]
            d1_text = f"{d1['label']} ({d1['actual_value']:.1f}, +{d1['abs_impact_pct']:.0f}% push)"
            d2_text = f"{pos_drivers[1]['label']} (+{pos_drivers[1]['abs_impact_pct']:.0f}% push)" if len(pos_drivers) > 1 else ""
            summary_drivers = f"{d1_text} and {d2_text}" if d2_text else d1_text
        else:
            summary_drivers = "nominal environmental baselines"
            
        road_pct = float(zone_row.get("road_connectivity_pct", 100.0))
        road_note = " ⚠️ Road access is SEVERED (<30%); direct ground vehicle dispatch blocked." if road_pct < 30.0 else ""
        
        commander_briefing = (
            f"COMMAND ADVISORY: {zone_id} ({zone_name}) is classified as {tier} with an Operational Priority Index of {opi:.1f}/100. "
            f"Triage prioritization is predominantly driven by {summary_drivers}.{road_note}"
        )
        
        return {
            "zone_id": zone_id,
            "zone_name": zone_name,
            "opi_score": opi,
            "triage_tier": tier,
            "top_drivers": top_drivers,
            "commander_briefing": commander_briefing
        }

    def explain_prediction(
        self,
        x_sample: Any,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Decomposes a single sample prediction into top risk drivers and percentage influence.
        Accepts dict, pd.Series, or 1-row pd.DataFrame.
        """
        if isinstance(x_sample, pd.DataFrame):
            df_sample = x_sample
            row_series = x_sample.iloc[0]
        elif isinstance(x_sample, pd.Series):
            df_sample = pd.DataFrame([x_sample])
            row_series = x_sample
        elif isinstance(x_sample, dict):
            df_sample = pd.DataFrame([x_sample])
            row_series = pd.Series(x_sample)
        else:
            df_sample = pd.DataFrame([x_sample])
            row_series = pd.Series(x_sample)

        # Ensure all FEATURE_COLUMNS are present
        for col in FEATURE_COLUMNS:
            if col not in df_sample.columns:
                df_sample[col] = 0.0

        shap_vals, _ = self.explain_zones(df_sample)
        attribution = self.get_zone_attribution(row_series, shap_vals[0], top_k=top_k)
        return attribution

    def generate_commander_brief(
        self,
        zone_data: Dict[str, Any],
        attribution: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generates or extracts automated AI commander briefing text.
        """
        if attribution and "commander_briefing" in attribution:
            return attribution["commander_briefing"]

        zone_id = zone_data.get("zone_id", "Sector")
        zone_name = zone_data.get("zone_name", zone_id)
        opi = float(zone_data.get("opi_score", 0.0))
        tier = zone_data.get("triage_tier", "Unspecified")
        return f"COMMAND ADVISORY: {zone_id} ({zone_name}) classified as {tier} with OPI {opi:.1f}/100. Emergency protocols active."
