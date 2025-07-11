# Known Bugs

1. **Client Name Clickability**: In the scenario, the client's name is not clickable to navigate to the client detail page. - COMPLETE

2. **Graph Formatting**: The top three graphs are not formatted correctly, affecting their display and usability. _ COMPLETED AND REMOVED

3. **Client Status Change Issue**: When starting with a client that is married and changing them to single, there is an issue with the scenario displaying correctly.

4. **FRA and Benefit Calculation**: When adding a new scenario, the Full Retirement Age (FRA) and the actual benefit based on the age need to be saved. A new field `FRA_amount` should be added to the `core_scenario` to store this value, and the `monthly_withdrawal` should be calculated based on the `FRA_amount`.

5. **IRMAA Box Color Issue**: The IRMAA box at the top of the ScenarioDetail is not changing color to reflect the circle graph in the Medicare tab. - COMPLETE

6. **Standard Deduction Not Applied**: Standard deductions do not appear to be applied in tax calculations, even when the toggle is enabled in the client/scenario setup. 

7. **AGI Too High Without Standard Deduction**: When you select NOT to apply standard deductions for a scenario, the AGI is much higher than expected (possibly due to calculation logic).

8. **Export Button Not Working**: The export button isn't working anywhere in the application. 

9. **Profile Links in Subdirectories**: When navigating to subdirectories (e.g., within client/scenario pages), the profile links in the top right corner of the application do not work correctly.

10. **Scenario creation page**: need to make sure we have medicare B and D inflation rates that are correct.

11. **Scenario creation page**: need to either fix or remove the tax scenario options.

12. **Scenario creation page**: need to make sure the reduction of social security toggle is working

13. **Scenario creation page**: need to check all the types of income are working

14. **Scenario creation page**: need to detect if there is a property, if they want to see, when they want to sell and assumed amount of equity when sold.

15. **Scenario creation page**: when you choose a lifespan over 90 it will stop the calcs at 90 but continue the blankn table of data

16. **GENERAL**: Always hitting too many requests... need to see where they are coming from

17. **Scenario creation page**: Selecting a state should be required when creating a scenario, as state tax calculations depend on this information.