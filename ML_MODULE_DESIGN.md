# Machine Learning Backend Module Design Specification

## 1. Purpose and Architecture

### 1.1 System Role
This Flask server functions as a dedicated machine learning backend service that:
- Integrates with an external Spring Boot application that owns the database and serves the frontend
- Processes ML training and prediction requests using scikit-learn
- Manages model lifecycle through database persistence

### 1.2 Integration Context
- **Primary Application**: Spring Boot service (database owner, frontend server, ML request mediator)
- **ML Backend**: This Flask application (model training, prediction, serialization)
- **Communication**: HTTP API between Spring Boot and Flask services

## 2. Model Management System

### 2.1 Model Registry
- Models are defined as Python classes in the `statistical/` directory
- Each model class must implement a standardized interface (see Section 4.1)
- Models are identified by a unique string `name` attribute
- Model availability is tracked in the database `models` table

### 2.2 Model States
- **Available**: Model exists in both codebase and database (`pipeline_ok = true`)
- **Unavailable**: Model exists in database but not in codebase (`pipeline_ok = false`)
- **Unregistered**: Model exists in codebase but not in database (warning logged)

## 3. Database Schema Requirements

### 3.1 Required Tables
* Note these tables all exist in the datasource in .env .  It is not necessary to create them.
```sql
models
(
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    type        VARCHAR(255) NOT NULL,
    description VARCHAR(1023),
    class_name  VARCHAR(511) NOT NULL,
    pipeline    BYTEA        NULL,
    features_ok BOOLEAN      NOT NULL,
    pipeline_ok BOOLEAN      NOT NULL,
    UNIQUE (name)
);

model_runs
(
    id         SERIAL PRIMARY KEY,
    model_id   BIGINT       NOT NULL REFERENCES models (id),
    run_date   TIMESTAMP    NOT NULL,
    run_status VARCHAR(255) NOT NULL,
    run_result BYTEA        NULL
);

model_run_metrics
(
    id           SERIAL PRIMARY KEY,
    model_run_id BIGINT NOT NULL REFERENCES model_runs (id),
    metric_name  VARCHAR(255),
    metric_value VARCHAR(255)
)
```

## 4. API Specification

### 4.1 Model Interface Requirements
Each model class in `statistical/` must implement:
```python
class ModelInterface:
    name: str  # Unique identifier
    
    def create_pipeline(self, parameters: dict) -> Pipeline:
        """Create sklearn Pipeline with given parameters"""
        pass
    
    def get_default_parameters(self) -> dict:
        """Return default parameter values"""
        pass
    
    def validate_features(self, features: Any) -> bool:
        """Validate input feature format"""
        pass
    
    def extract_metrics(self, pipeline: Pipeline, features: Any, labels: Any) -> dict:
        """Extract training metrics from fitted pipeline"""
        pass
```

### 4.2 Training Endpoint
**POST** `/api/train`

**Query Parameters:**
- `model_name` (required): String identifier for the model
- `model_run_id` (required): Integer ID for this training run

**Request Body:**
```json
{
    "parameters": {
        "param1": "value1",
        "param2": "value2"
    },
    "features": [
      {"col1":  "v", "col2":  "v"},
      {"col1":  "w", "col2":  "y"}
      ...
    ], 
    "labels": [
      {"feat":  "v"},
      {"feat":  "x"},
      ...
    ]   
}
```

**Response:**
- **200**: Training initiated successfully (asynchronous)
- **400**: Invalid model name or malformed request
- **500**: Internal server error

### 4.3 Prediction Endpoint
**POST** `/api/predict`

**Query Parameters:**
- `model_run_id` (required): Integer ID of trained model run

**Request Body:**
```json
{
    "features": [...]  // Prediction features (same format as training)
}
```

**Response:**
```json
{
    "predictions": [...],  // Model predictions
    "model_run_id": 123,
    "status": "success"
}
```

## 5. Workflow Details

### 5.1 Application Initialization
1. Scan `statistical/` directory for model classes
2. Query database `models` table for registered models
3. Update `pipeline_ok` status based on availability
4. Log warnings for unregistered models

### 5.2 Training Workflow
1. Receive POST request with model_name and model_run_id
2. Validate model exists and is available
3. Return 200 response immediately
4. **Asynchronously:**
   - Update `model_runs.run_status` to 'RUNNING'
   - Create pipeline with provided parameters
   - Train on features and labels
   - **On Success:**
     - Pickle trained pipeline to `model_runs.run_result`
     - Set `run_status` to 'SUCCESS'
     - Save metrics to `model_run_metrics`
   - **On Failure:**
     - Set `run_status` to 'FAILED'
     - Log error details

### 5.3 Prediction Workflow
1. Receive POST request with model_run_id
2. Query database for pickled pipeline
3. Deserialize pipeline object
4. Generate predictions on provided features
5. Return predictions as JSON

## 6. Areas Requiring Additional Information

### 6.1 Data Format Specifications
Response inline above

### 6.2 Error Handling and Logging
- **Training failures**: How to capture and store error details? Mark run as failure, and log the error verbosely  Potentially if there is more detail, we could save it in model_run_metrics.
- **Pipeline serialization**: Handling pickle failures or version compatibility -- IGNORE
- **Database connection**: Retry logic and connection pooling strategy -- IGNORE

### 6.3 Performance and Scalability
- **Asynchronous training**: A task queue is probably most well suited, but aim for simplicity.
- **Memory management**: We do not expect models of a size which would tax the limits.  Again we can ignore for now.
- **Concurrent requests**: This is a small system.  We will limit users to 1 concurrent request.

### 6.4 Security Considerations
- **Input validation**: Not considered.  Flask will be running in a container and not exposed outside of it.
- **Authentication**: Not considered.  Flask will be running in a conta
- **Data sanitization**: Let's require models to implement feature_names and label_names.  These can be compared to incoming feature and label sets.

### 6.5 Monitoring and Observability
- **Health checks**: Beyond basic `/api/health` endpoint
- **Metrics collection**: Training duration, prediction latency, model performance. Save for phase 2.
- **Logging strategy**: Structured logging for debugging and monitoring

## 7. Implementation Questions

1. **Database connection management**: Flask app should only connect to the database where it is explicitly detailed above.
2. **Model versioning**: At this point we are explicitly avoiding a versioning strategy.  There is no provision for users make breaking changes.
3. **Configuration management**: How are database credentials and other config passed to Flask app? The database url in in the existing .env .  No changes to the database schema should be necessary.
4. **Deployment coordination**: How to ensure Flask app and Spring Boot app stay synchronized?  Again there is no provision for that other that the initialization.