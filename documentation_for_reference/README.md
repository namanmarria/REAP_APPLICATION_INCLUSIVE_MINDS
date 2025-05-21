# REAP (Review, Evaluation, and Performance) Application

## Overview
REAP is a comprehensive performance evaluation system built with Django that enables organizations to conduct structured employee evaluations. The system supports multiple evaluation roles including Employee Self-Evaluation, Reporting Manager (RM) Evaluation, and Cross-Team Manager (CTM) Evaluation.

## Key Features
1. **Multi-level Evaluation Process**
   - Employee Self-Evaluation
   - Reporting Manager (RM) Evaluation
   - Cross-Team Manager (CTM) Evaluation
   - Program Manager (PGM) Evaluation

2. **Role-based Access Control**
   - Different views and permissions for each role
   - Secure access to evaluation forms
   - Hierarchical evaluation workflow

3. **Evaluation Management**
   - Create and manage evaluation cycles
   - Set evaluation periods with start and end dates
   - Track submission status
   - View evaluation history

4. **Question Management**
   - Support for different question types (Rating, Text)
   - Mandatory question marking
   - Sequential question ordering

5. **User Interface**
   - Responsive design
   - Interactive rating system
   - Real-time status updates
   - Progress tracking

## Technical Stack
- **Backend**: Django 4.2
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: PostgreSQL
- **Authentication**: Django Authentication System
- **Styling**: Bootstrap 5, Font Awesome

## Project Structure
```
REAP_APPLICATION/
├── authentication/     # Authentication related views and templates
├── core/              # Main application logic
├── static/            # Static files (CSS, JS, images)
├── templates/         # HTML templates
├── users/            # User management
└── reap_app1/        # Project configuration
```

## Installation and Setup

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd REAP_APPLICATION
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## Database Schema

### Key Models
1. **REAPCycle**
   - Manages evaluation cycles
   - Fields: name, start_date, end_date

2. **REAPQuestion**
   - Stores evaluation questions
   - Fields: question_text, question_type, is_mandatory, sequence

3. **REAPUserMapping**
   - Maps users to their roles in evaluations
   - Fields: user, rm, pgm, ctm, status

4. **REAPUserAnswer**
   - Stores user responses
   - Fields: answer_text, is_submit, submitted_user

## Workflow

1. **Evaluation Cycle Creation**
   - Admin creates evaluation cycle
   - Sets start and end dates
   - Configures questions

2. **Employee Self-Evaluation**
   - Employee completes self-evaluation
   - Submits for RM review

3. **RM Evaluation**
   - RM reviews employee submission
   - Provides evaluation
   - Submits for CTM review

4. **CTM Evaluation**
   - CTM reviews RM evaluation
   - Provides final evaluation
   - Completes the cycle

## Security Considerations

1. **Authentication**
   - Django's built-in authentication system
   - Session-based security
   - Password hashing

2. **Authorization**
   - Role-based access control
   - Permission checks at view level
   - Secure URL patterns

3. **Data Protection**
   - CSRF protection
   - SQL injection prevention
   - XSS protection

## Maintenance and Support

1. **Regular Updates**
   - Keep Django and dependencies updated
   - Monitor security advisories
   - Regular database backups

2. **Performance Optimization**
   - Database indexing
   - Query optimization
   - Caching strategies

3. **Monitoring**
   - Error logging
   - Performance monitoring
   - User activity tracking

## Troubleshooting

1. **Common Issues**
   - Database connection issues
   - Authentication problems
   - Form submission errors

2. **Debug Mode**
   - Enable debug mode in development
   - Check debug.log for errors
   - Use Django debug toolbar

## Future Enhancements

1. **Planned Features**
   - Email notifications
   - PDF report generation
   - Advanced analytics
   - Mobile app integration

2. **Performance Improvements**
   - API optimization
   - Frontend optimization
   - Database optimization

## Contact and Support

For technical support or questions, please contact:
- Email: [support-email]
- Documentation: [documentation-url]
- Issue Tracker: [issue-tracker-url] 