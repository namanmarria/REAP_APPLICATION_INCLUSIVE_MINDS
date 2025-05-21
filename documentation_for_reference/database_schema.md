# REAP Application Database Schema

## Overview
The REAP application uses MySQL as its database system. The schema is designed to support a multi-level evaluation system with role-based access control and comprehensive user management.

## Core Tables

### 1. auth_user
Base user table extending Django's authentication system.

```sql
CREATE TABLE auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined DATETIME NOT NULL
);
```

### 2. core_reapcycle
Manages evaluation cycles and their periods.

```sql
CREATE TABLE core_reapcycle (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### 3. core_reapquestion
Stores evaluation questions and their properties.

```sql
CREATE TABLE core_reapquestion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reap_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL,
    is_mandatory BOOLEAN NOT NULL,
    sequence INT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (reap_id) REFERENCES core_reapcycle(id)
);
```

### 4. core_reapusermapping
Maps users to their roles and relationships in evaluations.

```sql
CREATE TABLE core_reapusermapping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reap_id INT NOT NULL,
    user_id INT NOT NULL,
    rm_id INT,
    pgm_id INT,
    ctm_id INT,
    status VARCHAR(50) NOT NULL,
    user_submitted_at DATETIME,
    rm_submitted_at DATETIME,
    pgm_submitted_at DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (reap_id) REFERENCES core_reapcycle(id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    FOREIGN KEY (rm_id) REFERENCES auth_user(id),
    FOREIGN KEY (pgm_id) REFERENCES auth_user(id),
    FOREIGN KEY (ctm_id) REFERENCES auth_user(id)
);
```

### 5. core_reapuseranswer
Stores user responses to evaluation questions.

```sql
CREATE TABLE core_reapuseranswer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mapping_id INT NOT NULL,
    question_id INT NOT NULL,
    answer_text TEXT,
    is_submit BOOLEAN NOT NULL,
    submitted_user_id INT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (mapping_id) REFERENCES core_reapusermapping(id),
    FOREIGN KEY (question_id) REFERENCES core_reapquestion(id),
    FOREIGN KEY (submitted_user_id) REFERENCES auth_user(id)
);
```

## Indexes

### Primary Indexes
- All tables have an auto-incrementing `id` field as primary key
- Foreign key relationships are indexed automatically

### Secondary Indexes
```sql
-- core_reapusermapping indexes
CREATE INDEX idx_reap_user ON core_reapusermapping(reap_id, user_id);
CREATE INDEX idx_reap_status ON core_reapusermapping(reap_id, status);
CREATE INDEX idx_user_status ON core_reapusermapping(user_id, status);

-- core_reapuseranswer indexes
CREATE INDEX idx_mapping_question ON core_reapuseranswer(mapping_id, question_id);
CREATE INDEX idx_submitted_user ON core_reapuseranswer(submitted_user_id);
```

## Relationships

### One-to-Many Relationships
1. REAPCycle to REAPQuestion
   - One evaluation cycle can have multiple questions
   - Questions belong to one cycle

2. REAPCycle to REAPUserMapping
   - One cycle can have multiple user mappings
   - Each mapping belongs to one cycle

3. REAPUserMapping to REAPUserAnswer
   - One mapping can have multiple answers
   - Each answer belongs to one mapping

### Many-to-One Relationships
1. User to REAPUserMapping
   - One user can have multiple mappings
   - Each mapping belongs to one user

2. Question to REAPUserAnswer
   - One question can have multiple answers
   - Each answer belongs to one question

## Data Types

### Common Data Types
- `INT`: For IDs and sequence numbers
- `VARCHAR`: For short text fields
- `TEXT`: For long text content
- `DATETIME`: For timestamps
- `BOOLEAN`: For true/false flags
- `DATE`: For date-only fields

## Constraints

### Foreign Key Constraints
- All foreign keys have ON DELETE RESTRICT
- All foreign keys have ON UPDATE CASCADE

### Unique Constraints
- Username must be unique in auth_user
- Email must be unique in auth_user
- Combination of reap_id and user_id must be unique in core_reapusermapping

## Data Integrity

### Required Fields
- All primary keys
- All foreign keys
- Status fields
- Timestamp fields
- Name and text fields

### Default Values
- `is_active`: TRUE
- `is_staff`: FALSE
- `is_superuser`: FALSE
- `is_mandatory`: FALSE
- `is_submit`: FALSE

## Backup and Recovery

### Backup Strategy
- Daily full database backup
- Transaction log backup every hour
- Point-in-time recovery capability

### Recovery Procedures
1. Full database restore
2. Transaction log replay
3. Data consistency check

## Performance Considerations

### Query Optimization
- Indexed fields for common queries
- Optimized join operations
- Efficient subqueries

### Maintenance
- Regular index optimization
- Table statistics updates
- Query cache management 