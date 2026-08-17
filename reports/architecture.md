# AutonomousAI — System Architecture Diagram

```mermaid
graph TD
    Client([Web Client / Browser]) --> Router[FastAPI Router]
    Router --> HealthAPI[/api/health]
    Router --> RootAPI[/]
    Router --> UI[Frontend View]
```

*Generated on demand via `autonomous report --architecture`.*
