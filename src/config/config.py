config = {
    
    "kafka": {
        "sasl.username": "",
        "sasl.password": "",
        "bootstrap.servers": "pkc-619z3.us-east1.gcp.confluent.cloud:9092",
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'PLAIN',
        'session.timeout.ms': 50000
    },
    "schema_registry": {
        "url": "SCHEMA_REGISTRY_URL",
        "basic.auth.user.info": "SR_API_KEY:SR_API_SECRET"

    }
    
}