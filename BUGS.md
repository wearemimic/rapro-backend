# Known Bugs

1. **Client Name Clickability**: In the scenario, the client's name is not clickable to navigate to the client detail page.

2. **Graph Formatting**: The top three graphs are not formatted correctly, affecting their display and usability.

3. **Client Status Change Issue**: When starting with a client that is married and changing them to single, there is an issue with the scenario displaying correctly.

4. **FRA and Benefit Calculation**: When adding a new scenario, the Full Retirement Age (FRA) and the actual benefit based on the age need to be saved. A new field `FRA_amount` should be added to the `core_scenario` to store this value, and the `monthly_withdrawal` should be calculated based on the `FRA_amount`. 