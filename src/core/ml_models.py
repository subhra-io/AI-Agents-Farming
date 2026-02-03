"""
Machine Learning models for crop and yield prediction using XGBoost with caching
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
import pickle
import os
from datetime import datetime
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, accuracy_score
from ..core.cache_service import cache_ml_prediction, get_cached_ml_prediction


class CropYieldPredictor:
    """XGBoost-based crop yield prediction model"""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.yield_model = None
        self.crop_model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = [
            'temperature', 'humidity', 'precipitation', 'ph', 'organic_matter',
            'latitude', 'longitude', 'month', 'soil_type_encoded'
        ]
        
        # Create models directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        
        # Try to load existing models
        self._load_models()
    
    def prepare_features(
        self, 
        weather_data: Dict[str, Any],
        soil_data: Dict[str, Any],
        location_data: Dict[str, Any]
    ) -> np.ndarray:
        """Prepare feature vector for ML prediction"""
        
        # Extract features
        features = {
            'temperature': weather_data.get('temperature', 20),
            'humidity': weather_data.get('humidity', 60),
            'precipitation': weather_data.get('precipitation', 0),
            'ph': self._extract_ph_value(soil_data.get('ph_range', (6.5, 6.5))),
            'organic_matter': self._extract_om_value(soil_data.get('organic_matter_percent', (3, 3))),
            'latitude': location_data.get('latitude', 0),
            'longitude': location_data.get('longitude', 0),
            'month': datetime.now().month,
            'soil_type_encoded': self._encode_soil_type(soil_data.get('primary_soil_type', 'mollisol'))
        }
        
        # Convert to array in correct order
        feature_array = np.array([features[name] for name in self.feature_names]).reshape(1, -1)
        
        return feature_array
    
    def predict_yield(
        self,
        crop_name: str,
        weather_data: Dict[str, Any],
        soil_data: Dict[str, Any],
        location_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict crop yield using trained model with caching"""
        
        # Check cache first (1 hour TTL)
        cached_result = get_cached_ml_prediction(crop_name, location_data.get('latitude', 0), location_data.get('longitude', 0))
        if cached_result:
            cached_result['cached'] = True
            return cached_result
        
        if self.yield_model is None:
            # Use rule-based prediction if no trained model
            result = self._rule_based_yield_prediction(crop_name, weather_data, soil_data)
            result['cached'] = False
            cache_ml_prediction(crop_name, location_data.get('latitude', 0), location_data.get('longitude', 0), result)
            return result
        
        try:
            features = self.prepare_features(weather_data, soil_data, location_data)
            features_scaled = self.scaler.transform(features)
            
            # Predict yield
            predicted_yield = self.yield_model.predict(features_scaled)[0]
            
            # Get feature importance for explanation
            feature_importance = dict(zip(
                self.feature_names,
                self.yield_model.feature_importances_
            ))
            
            result = {
                'predicted_yield_kg_per_hectare': max(0, predicted_yield),
                'confidence': self._calculate_prediction_confidence(features_scaled),
                'feature_importance': feature_importance,
                'model_used': 'xgboost',
                'cached': False
            }
            
            # Cache the result
            cache_ml_prediction(crop_name, location_data.get('latitude', 0), location_data.get('longitude', 0), result)
            return result
            
        except Exception as e:
            print(f"ML prediction error: {e}")
            result = self._rule_based_yield_prediction(crop_name, weather_data, soil_data)
            result['cached'] = False
            cache_ml_prediction(crop_name, location_data.get('latitude', 0), location_data.get('longitude', 0), result)
            return result
    
    def predict_best_crops(
        self,
        weather_data: Dict[str, Any],
        soil_data: Dict[str, Any],
        location_data: Dict[str, Any],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """Predict best crops for given conditions"""
        
        if self.crop_model is None:
            return self._rule_based_crop_prediction(weather_data, soil_data, location_data, top_n)
        
        try:
            features = self.prepare_features(weather_data, soil_data, location_data)
            features_scaled = self.scaler.transform(features)
            
            # Get crop probabilities
            crop_probabilities = self.crop_model.predict_proba(features_scaled)[0]
            crop_names = self.crop_model.classes_
            
            # Sort by probability
            crop_scores = list(zip(crop_names, crop_probabilities))
            crop_scores.sort(key=lambda x: x[1], reverse=True)
            
            results = []
            for crop_name, probability in crop_scores[:top_n]:
                results.append({
                    'crop_name': crop_name,
                    'suitability_probability': probability,
                    'confidence': probability
                })
            
            return results
            
        except Exception as e:
            print(f"ML crop prediction error: {e}")
            return self._rule_based_crop_prediction(weather_data, soil_data, location_data, top_n)
    
    def train_models(self, training_data: Optional[pd.DataFrame] = None):
        """Train XGBoost models with real or synthetic data"""
        
        if training_data is None:
            # Try to load real data first
            try:
                from ..data.real_yield_data import get_real_training_data
                training_data = get_real_training_data()
                print("🎯 Using REAL yield data for training")
            except Exception as e:
                print(f"⚠️  Real data not available ({e}), using synthetic data")
                training_data = self._generate_synthetic_training_data()
        
        # Prepare features and targets
        X = training_data[self.feature_names].values
        y_yield = training_data['yield'].values
        y_crop = training_data['crop_name'].values
        
        # Split data
        X_train, X_test, y_yield_train, y_yield_test, y_crop_train, y_crop_test = train_test_split(
            X, y_yield, y_crop, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Encode crop labels
        y_crop_encoded = self.label_encoder.fit_transform(y_crop_train)
        
        # Train yield prediction model
        self.yield_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.yield_model.fit(X_train_scaled, y_yield_train)
        
        # Train crop classification model
        self.crop_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.crop_model.fit(X_train_scaled, y_crop_encoded)
        
        # Evaluate models
        yield_pred = self.yield_model.predict(X_test_scaled)
        crop_pred = self.crop_model.predict(X_test_scaled)
        
        yield_rmse = np.sqrt(mean_squared_error(y_yield_test, yield_pred))
        crop_accuracy = accuracy_score(self.label_encoder.transform(y_crop_test), crop_pred)
        
        print(f"Yield Model RMSE: {yield_rmse:.2f}")
        print(f"Crop Model Accuracy: {crop_accuracy:.3f}")
        
        # Save models
        self._save_models()
    
    def _generate_synthetic_training_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """Generate synthetic training data for model training"""
        
        from ..data.crop_database import CropDatabase
        crop_db = CropDatabase()
        
        np.random.seed(42)
        data = []
        
        for _ in range(n_samples):
            # Random location
            lat = np.random.uniform(-60, 60)
            lon = np.random.uniform(-180, 180)
            
            # Random environmental conditions
            temp = np.random.uniform(5, 40)
            humidity = np.random.uniform(20, 90)
            precip = np.random.uniform(0, 20)
            ph = np.random.uniform(4.5, 8.5)
            om = np.random.uniform(0.5, 10)
            month = np.random.randint(1, 13)
            
            # Random soil type
            soil_types = ['mollisol', 'alfisol', 'ultisol', 'aridisol', 'inceptisol']
            soil_type = np.random.choice(soil_types)
            
            # Select random crop and calculate yield based on suitability
            crop_name = np.random.choice(crop_db.get_all_crops())
            crop_info = crop_db.get_crop_info(crop_name)
            
            # Calculate yield based on crop requirements
            yield_base = np.mean(crop_info.get('yield_potential', (1000, 5000)))
            
            # Apply environmental factors
            temp_range = crop_info.get('optimal_temperature', (20, 25))
            temp_factor = 1.0 if temp_range[0] <= temp <= temp_range[1] else 0.5
            
            ph_range = crop_info.get('ph_range', (6.0, 7.0))
            ph_factor = 1.0 if ph_range[0] <= ph <= ph_range[1] else 0.7
            
            # Random variation
            random_factor = np.random.uniform(0.7, 1.3)
            
            final_yield = yield_base * temp_factor * ph_factor * random_factor
            
            data.append({
                'temperature': temp,
                'humidity': humidity,
                'precipitation': precip,
                'ph': ph,
                'organic_matter': om,
                'latitude': lat,
                'longitude': lon,
                'month': month,
                'soil_type_encoded': self._encode_soil_type(soil_type),
                'crop_name': crop_name,
                'yield': final_yield
            })
        
        return pd.DataFrame(data)
    
    def _extract_ph_value(self, ph_range) -> float:
        """Extract single pH value from range"""
        if isinstance(ph_range, (tuple, list)):
            return sum(ph_range) / 2
        return float(ph_range)
    
    def _extract_om_value(self, om_range) -> float:
        """Extract single organic matter value from range"""
        if isinstance(om_range, (tuple, list)):
            return sum(om_range) / 2
        return float(om_range)
    
    def _encode_soil_type(self, soil_type: str) -> int:
        """Encode soil type as integer"""
        soil_mapping = {
            'mollisol': 1, 'alfisol': 2, 'ultisol': 3, 'aridisol': 4,
            'inceptisol': 5, 'oxisol': 6, 'vertisol': 7, 'gelisol': 8,
            'spodosol': 9, 'entisol': 10, 'laterite': 11
        }
        return soil_mapping.get(soil_type.lower(), 1)
    
    def _calculate_prediction_confidence(self, features: np.ndarray) -> float:
        """Calculate confidence score for prediction"""
        # Simple confidence based on feature values being within normal ranges
        confidence = 0.8  # Base confidence
        
        # Adjust based on extreme values
        if np.any(np.abs(features) > 3):  # Standardized values > 3 std devs
            confidence *= 0.7
        
        return confidence
    
    def _rule_based_yield_prediction(
        self, 
        crop_name: str, 
        weather_data: Dict[str, Any], 
        soil_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback rule-based yield prediction"""
        
        from ..data.crop_database import CropDatabase
        crop_db = CropDatabase()
        
        crop_info = crop_db.get_crop_info(crop_name)
        if not crop_info:
            return {'predicted_yield_kg_per_hectare': 0, 'confidence': 0.1, 'model_used': 'fallback'}
        
        base_yield = np.mean(crop_info.get('yield_potential', (1000, 5000)))
        
        # Simple environmental factors
        temp = weather_data.get('temperature', 20)
        temp_range = crop_info.get('optimal_temperature', (20, 25))
        temp_factor = 1.0 if temp_range[0] <= temp <= temp_range[1] else 0.7
        
        predicted_yield = base_yield * temp_factor
        
        return {
            'predicted_yield_kg_per_hectare': predicted_yield,
            'confidence': 0.6,
            'model_used': 'rule_based'
        }
    
    def _rule_based_crop_prediction(
        self,
        weather_data: Dict[str, Any],
        soil_data: Dict[str, Any],
        location_data: Dict[str, Any],
        top_n: int
    ) -> List[Dict[str, Any]]:
        """Fallback rule-based crop prediction"""
        
        from ..data.crop_database import CropDatabase
        crop_db = CropDatabase()
        
        climate_zone = soil_data.get('climate_zone', 'temperate')
        suitable_crops = crop_db.get_crops_by_climate(climate_zone)
        
        results = []
        for i, crop in enumerate(suitable_crops[:top_n]):
            results.append({
                'crop_name': crop,
                'suitability_probability': 0.8 - (i * 0.1),
                'confidence': 0.6
            })
        
        return results
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            if self.yield_model:
                pickle.dump(self.yield_model, open(f"{self.model_dir}/yield_model.pkl", "wb"))
            if self.crop_model:
                pickle.dump(self.crop_model, open(f"{self.model_dir}/crop_model.pkl", "wb"))
            pickle.dump(self.scaler, open(f"{self.model_dir}/scaler.pkl", "wb"))
            pickle.dump(self.label_encoder, open(f"{self.model_dir}/label_encoder.pkl", "wb"))
            print("Models saved successfully")
        except Exception as e:
            print(f"Error saving models: {e}")
    
    def _load_models(self):
        """Load trained models from disk"""
        try:
            if os.path.exists(f"{self.model_dir}/yield_model.pkl"):
                self.yield_model = pickle.load(open(f"{self.model_dir}/yield_model.pkl", "rb"))
            if os.path.exists(f"{self.model_dir}/crop_model.pkl"):
                self.crop_model = pickle.load(open(f"{self.model_dir}/crop_model.pkl", "rb"))
            if os.path.exists(f"{self.model_dir}/scaler.pkl"):
                self.scaler = pickle.load(open(f"{self.model_dir}/scaler.pkl", "rb"))
            if os.path.exists(f"{self.model_dir}/label_encoder.pkl"):
                self.label_encoder = pickle.load(open(f"{self.model_dir}/label_encoder.pkl", "rb"))
            print("Models loaded successfully")
        except Exception as e:
            print(f"Error loading models: {e}")
            # Initialize fresh models if loading fails
            self.yield_model = None
            self.crop_model = None