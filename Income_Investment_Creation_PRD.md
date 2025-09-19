# Product Requirements Document: Income Source & Investment Asset Creation System

## Overview

This PRD provides comprehensive technical specifications for implementing a complete income source and investment asset creation system within a retirement planning application. The system enables financial advisors to create, edit, and manage client retirement scenarios with sophisticated income and investment modeling.

## System Architecture

### Technology Stack
- **Backend**: Django 4.2 with Django REST Framework
- **Frontend**: Vue.js 3 with Composition API
- **Database**: PostgreSQL
- **Authentication**: JWT tokens via Auth0

### Core Data Models

#### IncomeSource Model
```python
class IncomeSource(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='income_sources')
    
    # Ownership
    OWNED_BY_CHOICES = [('primary', 'Primary'), ('spouse', 'Spouse')]
    owned_by = models.CharField(max_length=10, choices=OWNED_BY_CHOICES)
    
    # Basic Information
    income_type = models.CharField(max_length=200)  # Type of income (Social Security, Pension, etc.)
    income_name = models.CharField(max_length=50)   # Custom name for the income source
    
    # Financial Data
    current_asset_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monthly_contribution = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Age-based Controls
    age_to_begin_withdrawal = models.PositiveIntegerField(null=True, blank=True)
    age_to_end_withdrawal = models.PositiveIntegerField()
    age_established = models.PositiveIntegerField(null=True, blank=True)
    
    # Financial Parameters
    rate_of_return = models.FloatField(default=0)        # Investment growth rate
    cola = models.FloatField(default=0)                  # Cost of living adjustment
    exclusion_ratio = models.FloatField(default=0)       # Tax exclusion percentage
    tax_rate = models.FloatField(default=0)              # Tax rate applied
    
    # Investment-specific Fields
    max_to_convert = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, 
                                       help_text="Maximum amount to convert to Roth")
    is_contributing = models.BooleanField(default=False, help_text="Currently contributing to this investment")
```

---

## Phase 1: Database & Backend Infrastructure

### Task 1.1: Database Schema Implementation
- [ ] Create IncomeSource model with all specified fields
- [ ] Set up foreign key relationship to Scenario model
- [ ] Create database indexes for performance optimization
- [ ] Implement model validation rules for financial data
- [ ] Create Django migrations for schema deployment

### Task 1.2: API Serializers
- [ ] Implement IncomeSourceSerializer for CRUD operations
- [ ] Create IncomeSourceCreateSerializer with validation
- [ ] Implement IncomeSourceUpdateSerializer for editing
- [ ] Add field validation for currency amounts and percentages
- [ ] Implement custom validation for age ranges and financial logic

### Task 1.3: API Endpoints
- [ ] `POST /api/clients/{client_id}/scenarios/create/` - Create scenario with income sources
- [ ] `GET /api/scenarios/{scenario_id}/income-sources/` - List all income sources
- [ ] `POST /api/scenarios/{scenario_id}/income-sources/` - Add new income source
- [ ] `PUT /api/scenarios/{scenario_id}/income-sources/{id}/` - Update income source
- [ ] `DELETE /api/scenarios/{scenario_id}/income-sources/{id}/` - Delete income source
- [ ] Implement proper authentication and authorization
- [ ] Add request/response validation and error handling

---

## Phase 2: Frontend Components & UI

### Task 2.1: Income Management Interface
- [ ] Create income type dropdown with predefined options:
  - Social Security
  - Pension
  - Wages
  - Rental Income
  - Other
- [ ] Implement "Add Income Product" button functionality
- [ ] Create grouped income display by income type
- [ ] Implement responsive table layout for income display

### Task 2.2: Dynamic Form Fields by Income Type

#### Social Security Forms
- [ ] Amount at FRA input field with currency formatting
- [ ] Start age dropdown (62-70 years)
- [ ] COLA percentage input
- [ ] Actual benefit amount calculation display
- [ ] Medicare adjustment integration

#### Pension Forms
- [ ] Monthly income input with currency formatting
- [ ] COLA percentage input
- [ ] Start age selection
- [ ] Owner selection (Primary/Spouse)

#### Wages/Salary Forms
- [ ] Monthly amount input with currency formatting
- [ ] Start age and end age dropdowns
- [ ] Owner selection (Primary/Spouse)

#### Investment Account Forms (Traditional IRA, Roth IRA, 401k)
- [ ] Current balance input with currency formatting
- [ ] Monthly contribution input
- [ ] Growth rate percentage input
- [ ] Start age for withdrawals
- [ ] Monthly withdrawal amount input
- [ ] Age asset was established

### Task 2.3: Investment Modal System
- [ ] Create InvestmentModal.vue component
- [ ] Implement modal show/hide functionality
- [ ] Create investment form with all required fields:
  - Account Owner selection
  - Account Type dropdown (Qualified, Non-Qualified, Roth, Inherited options)
  - Investment Name input
  - Current Balance with currency formatting
  - Age Asset Established dropdown
  - Estimated Rate of Return percentage input
  - Age to Begin/End Withdrawals dropdowns
  - Minimum Monthly Withdrawal input
  - Contributing checkbox with conditional fields
  - Annual Contribution Amount (when contributing)
  - Employer Match percentage
  - Age Last Year of Contribution

### Task 2.4: Currency Formatting System
- [ ] Implement formatCurrency() utility function
- [ ] Create onCurrencyInput() handler for real-time formatting
- [ ] Implement onCurrencyFocus() for editing mode
- [ ] Create onCurrencyBlur() for display formatting
- [ ] Handle edge cases (empty values, decimals, large numbers)

---

## Phase 3: Business Logic & Validation

### Task 3.1: Age Calculation Logic
- [ ] Implement dynamic age range calculations based on:
  - Client current age from birthdate
  - Primary/spouse lifespan settings
  - Income type constraints
  - Retirement age settings
- [ ] Create age validation for logical constraints
- [ ] Implement age dropdown population based on ownership

### Task 3.2: Social Security Benefit Calculations
- [ ] Implement calculateSocialSecurityBenefit() function
- [ ] Apply early/delayed retirement adjustment factors
- [ ] Calculate actual benefit amount from FRA amount
- [ ] Integrate COLA adjustments over time

### Task 3.3: Investment Growth Calculations
- [ ] Implement compound growth calculations
- [ ] Apply monthly contributions with employer matching
- [ ] Calculate withdrawal amounts based on age ranges
- [ ] Apply rate of return to investment balances

### Task 3.4: Form Validation
- [ ] Required field validation
- [ ] Numeric range validation for percentages (0-100%)
- [ ] Currency amount validation (positive values, reasonable limits)
- [ ] Age range logical validation (start < end)
- [ ] Cross-field validation (contribution vs. withdrawal ages)

---

## Phase 4: Data Integration & Storage

### Task 4.1: Scenario Creation Flow
- [ ] Integrate income sources into scenario creation
- [ ] Implement investment data transformation for API payload
- [ ] Handle both income sources and investment accounts in single scenario
- [ ] Implement proper data mapping between frontend and backend models

### Task 4.2: Edit Mode Implementation
- [ ] Detect edit mode from URL parameters
- [ ] Populate forms with existing scenario data
- [ ] Implement update API calls for modifications
- [ ] Handle data transformation for editing existing records

### Task 4.3: Data Persistence
- [ ] Implement proper save functionality for all income types
- [ ] Handle investment modal save with proper data formatting
- [ ] Implement remove/delete functionality with confirmation
- [ ] Add error handling for failed save operations

---

## Phase 5: Advanced Features

### Task 5.1: Investment Account Integration
- [ ] Create investment accounts as specialized income sources
- [ ] Implement investment-specific business logic
- [ ] Handle qualified vs. non-qualified account rules
- [ ] Implement Roth conversion capabilities

### Task 5.2: Tax Integration
- [ ] Apply appropriate tax rates by income type
- [ ] Implement tax exclusion ratios for annuities
- [ ] Calculate taxable vs. non-taxable income portions
- [ ] Integrate with federal/state tax calculation system

### Task 5.3: Reporting Integration
- [ ] Format income/investment data for financial reports
- [ ] Calculate projected income streams over time
- [ ] Generate investment growth projections
- [ ] Export data for PDF/PowerPoint reports

---

## Technical Implementation Details

### API Request/Response Format

#### Create Income Source
```json
POST /api/scenarios/{scenario_id}/income-sources/
{
  "income_type": "social_security",
  "owned_by": "primary",
  "income_name": "Primary SS",
  "monthly_amount": 3500.00,
  "age_to_begin_withdrawal": 67,
  "age_to_end_withdrawal": 90,
  "cola": 2.5,
  "tax_rate": 0.15
}
```

#### Investment Account Data Structure
```json
{
  "income_type": "Traditional_401k",
  "investment_name": "Company 401k",
  "owned_by": "primary",
  "current_balance": 125000.00,
  "rate_of_return": 0.07,
  "age_established": 25,
  "start_age": 65,
  "end_age": 90,
  "monthly_withdrawal_amount": 2500.00,
  "is_contributing": true,
  "annual_contribution_amount": 19500.00,
  "employer_match": 3.5,
  "age_last_contribution": 67
}
```

### Frontend Component Structure
```
ScenarioCreate.vue
├── Income Management Section
│   ├── Income Type Dropdown
│   ├── Add Income Button
│   └── Grouped Income Tables
│       ├── Social Security Table
│       ├── Pension Table
│       ├── Wages Table
│       ├── Investment Tables
│       └── Other Income Table
├── Investment Section
│   ├── Add Investment Button
│   ├── Investment Display Table
│   └── Investment Modal
└── InvestmentModal.vue
    ├── Account Information Form
    ├── Financial Details Form
    ├── Age-based Controls
    ├── Contribution Section
    └── Save/Cancel Actions
```

### Validation Rules Summary
- **Currency Fields**: Positive values, max 12 digits, 2 decimal places
- **Percentage Fields**: 0-100%, max 2 decimal places
- **Age Fields**: Logical ranges based on owner lifespan
- **Required Fields**: Income type, investment name, owner selection
- **Cross-validation**: Start age < End age, contribution age < retirement age

---

## Testing Requirements

### Unit Tests
- [ ] Model validation tests
- [ ] Serializer validation tests
- [ ] API endpoint tests
- [ ] Currency formatting tests
- [ ] Age calculation tests

### Integration Tests
- [ ] Complete scenario creation flow
- [ ] Income source CRUD operations
- [ ] Investment modal functionality
- [ ] Data persistence verification

### User Acceptance Tests
- [ ] Create various income types successfully
- [ ] Edit existing income sources
- [ ] Create and manage investment accounts
- [ ] Validate all form inputs and error handling
- [ ] Verify calculation accuracy

---

## Performance Requirements
- API response time < 200ms for CRUD operations
- Frontend form updates < 50ms for currency formatting
- Support 50+ income sources per scenario
- Handle concurrent editing by multiple users

## Security Requirements
- JWT authentication for all API endpoints
- Input sanitization for all user data
- Rate limiting on creation endpoints
- Data validation on both client and server side

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

This PRD provides complete specifications for implementing a production-ready income source and investment asset creation system that can be fully implemented by another development team from scratch.