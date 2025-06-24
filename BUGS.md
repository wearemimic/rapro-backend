# Known Bugs

1. **Client Name Clickability**: In the scenario, the client's name is not clickable to navigate to the client detail page. - COMPLETE

2. **Graph Formatting**: The top three graphs are not formatted correctly, affecting their display and usability. _ COMPLETED AND REMOVED

3. **Client Status Change Issue**: When starting with a client that is married and changing them to single, there is an issue with the scenario displaying correctly.

4. **FRA and Benefit Calculation**: When adding a new scenario, the Full Retirement Age (FRA) and the actual benefit based on the age need to be saved. A new field `FRA_amount` should be added to the `core_scenario` to store this value, and the `monthly_withdrawal` should be calculated based on the `FRA_amount`.

5. **IRMAA Box Color Issue**: The IRMAA box at the top of the ScenarioDetail is not changing color to reflect the circle graph in the Medicare tab. 

6. **Standard Deduction Not Applied**: Standard deductions do not appear to be applied in tax calculations, even when the toggle is enabled in the client/scenario setup. 

7. **AGI Too High Without Standard Deduction**: When you select NOT to apply standard deductions for a scenario, the AGI is much higher than expected (possibly due to calculation logic).

8. **Export Button Not Working**: The export button isn't working anywhere in the application. 