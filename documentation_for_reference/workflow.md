# REAP Application Workflow

## Evaluation Process Flow

```mermaid
graph TD
    A[Start Evaluation Cycle] --> B[Admin Creates Cycle]
    B --> C[Set Questions & Dates]
    C --> D[Employee Self-Evaluation]
    D --> E{Employee Submits?}
    E -->|No| D
    E -->|Yes| F[RM Evaluation]
    F --> G{RM Submits?}
    G -->|No| F
    G -->|Yes| H[CTM Evaluation]
    H --> I{CTM Submits?}
    I -->|No| H
    I -->|Yes| J[Cycle Complete]
```

## User Role Hierarchy

```mermaid
graph TD
    A[Admin] --> B[Employee]
    A --> C[Reporting Manager]
    A --> D[Cross-Team Manager]
    C --> B
    D --> C
```

## Evaluation Form States

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Saved
    Saved --> Draft
    Saved --> Submitted
    Submitted --> [*]
```

## Database Relationships

```mermaid
erDiagram
    REAPCycle ||--o{ REAPQuestion : contains
    REAPCycle ||--o{ REAPUserMapping : has
    REAPUserMapping ||--o{ REAPUserAnswer : contains
    User ||--o{ REAPUserMapping : participates
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as Auth System
    participant V as View
    participant D as Database

    U->>A: Login Request
    A->>D: Verify Credentials
    D->>A: Return User Data
    A->>V: Set Session
    V->>U: Redirect to Dashboard
```

## Evaluation Submission Process

```mermaid
sequenceDiagram
    participant E as Employee
    participant RM as Reporting Manager
    participant CTM as Cross-Team Manager
    participant S as System

    E->>S: Submit Self-Evaluation
    S->>RM: Notify RM
    RM->>S: Review & Submit
    S->>CTM: Notify CTM
    CTM->>S: Final Review & Submit
    S->>S: Mark Cycle Complete
```

## Error Handling Flow

```mermaid
graph TD
    A[Error Occurs] --> B{Error Type}
    B -->|Validation| C[Show Form Errors]
    B -->|Permission| D[Show Access Denied]
    B -->|System| E[Show Error Page]
    C --> F[Return to Form]
    D --> G[Redirect to Login]
    E --> H[Log Error]
``` 