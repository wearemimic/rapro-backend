# Enhancements

## 1. Update `start.sh` Script

- **Objective**: Modify the `start.sh` script to include a check for any running processes on a specified port before proceeding with the build.
- **Details**: This enhancement will help prevent port conflicts by ensuring that no other services are running on the required port before starting the build process. If a process is found running on the port, the script should prompt the user to stop the process or choose a different port.
- **Implementation Steps**:
  1. Add a function in `start.sh` to check for running processes on the specified port using a command like `lsof -i :<port>`.
  2. If a process is found, output a message to the user indicating the conflict and provide options to resolve it.
  3. Proceed with the build only if the port is free or after the user resolves the conflict.

## 2. Show Graph for Asset Income

- **Objective**: When adding income, if it is a Asset like a 401k, display a graph showing the spend down based on criteria and the amount left at death.
- **Details**: This enhancement will provide a visual representation of how the masset is spent over time, helping users understand the financial trajectory and remaining balance at the end of life.
- **Implementation Steps**:
  1. Identify when the income source is a asset like a 401k during the income addition process.
  2. Calculate the spend down trajectory based on user-defined criteria.
  3. Display a graph under the income entry showing the spend down and the projected amount left at death.

## 3. Model Different Income Withdrawal Levels

- **Objective**: Allow users to specify different income withdrawal levels over time for accounts like Roth IRA.
- **Details**: This enhancement will enable users to model scenarios where they withdraw different amounts at different stages of retirement. For example, withdrawing $4,000 a month for the first 3 years, then $3,000 for the remainder of retirement.
- **Implementation Steps**:
  1. Update the income modeling interface to allow users to specify multiple withdrawal levels and durations.
  2. Adjust the simulation engine to account for these varying withdrawal levels over the specified periods.
  3. Ensure the results reflect the impact of these changes on the overall retirement plan and account balances.

## 4. Analyze Wealthbox Clients for IRMAA Impact

- **Objective**: Use AI to analyze clients in Wealthbox and identify those who may be hitting IRMAA based on their assets.
- **Details**: This enhancement will leverage AI to automatically review client data in Wealthbox, assessing asset levels and predicting potential IRMAA impacts. This proactive approach helps advisors manage client expectations and plan accordingly.
- **Implementation Steps**:
  1. Integrate Wealthbox API to access client data securely.
  2. Develop an AI model to analyze asset data and predict IRMAA impact.
  3. Provide a report or dashboard highlighting clients at risk of IRMAA, with recommendations for mitigation.

## 5. Update Button Text and Default Scenario Name for First Scenario

- **Objective**: Change the button text to "Run your First Stress Test" on the client detail page for the first scenario, and default the scenario name to "IRMAA Stress Test" on the scenario creation page for the first scenario.
- **Details**: This enhancement aims to guide users through their first scenario setup by providing clear instructions and a default scenario name.
- **Implementation Steps**:
  1. Detect when the user is running their first scenario on the client detail page.
  2. Update the button text to "Run your First Stress Test" for the first scenario.
  3. On the scenario creation page, set the default scenario name to "IRMAA Stress Test" for the first scenario.
  4. Ensure these changes only apply to the first scenario and revert to standard behavior for subsequent scenarios.

## 6. Add Age Sliders and Heat Map for Social Security Timing

- **Objective**: Introduce sliders above the graphs to allow users to select ages for the client and spouse, showing the impact of taxes, IRMAA, etc., based on the chosen age for social security. Additionally, implement a heat map to indicate the optimal time for taking social security.
- **Details**: This enhancement will provide an interactive way for users to visualize the financial impact of different social security claiming ages. The heat map will help users identify the best time to claim social security benefits.
- **Implementation Steps**:
  1. Add sliders above the graphs for selecting the ages of the client and spouse.
  2. Update the graphs dynamically to reflect changes in taxes, IRMAA, and other financial metrics based on the selected ages.
  3. Develop a heat map to display the optimal social security claiming age, considering various financial factors.
  4. Ensure the user interface is intuitive and provides clear insights into the financial implications of different age selections.

## 7. Include Social Security Rules for Spousal Claiming Strategies

- **Objective**: Integrate social security rules to provide guidance on optimal spousal claiming strategies.
- **Details**: This enhancement will help users understand the best strategies for a spouse to claim social security benefits, taking into account various rules and scenarios.
- **Implementation Steps**:
  1. Research and compile relevant social security rules and strategies for spousal benefits.
  2. Implement logic to analyze user data and suggest optimal claiming strategies for spouses.
  3. Display recommendations and potential outcomes in the user interface, providing clear guidance on spousal claiming options.
  4. Ensure the recommendations are personalized based on the user's specific financial situation and goals.

## 8. Add Table to Compare Benefits at Full Retirement Age (FRA) and Other Ages

- **Objective**: Provide a table under the age slider to display the social security benefits at Full Retirement Age (FRA) and compare them with benefits at other selected ages.
- **Details**: This enhancement will allow users to see the difference in social security benefits between the FRA and any other age they choose using the slider.
- **Implementation Steps**:
  1. Create a table component to display social security benefits at FRA and other selected ages.
  2. Update the table dynamically as users adjust the age slider, showing the difference in benefits.
  3. Ensure the table provides clear and concise information, helping users make informed decisions about when to claim benefits.
  4. Integrate the table with the existing slider and graph components for a seamless user experience.

## 9. Access to Social Security Forms and Wealthbox Reminders for IRMAA

- **Objective**: Provide access to all forms related to social security and set reminders in Wealthbox for IRMAA preparation, including having the SSA-44 form ready.
- **Details**: This enhancement will ensure users have easy access to necessary social security forms and are reminded to prepare for IRMAA two years prior to retirement.
- **Implementation Steps**:
  1. Compile a list of all relevant social security forms and make them accessible within the application.
  2. Integrate with Wealthbox to set reminders for users two years before retirement to prepare for IRMAA.
  3. Ensure the SSA-44 form is readily available for users to fill out and submit.
  4. Provide clear instructions and guidance on how to use these forms and reminders effectively.

## 10. Allow Asset Labeling for Easy Identification

- **Objective**: Enable users to assign labels to assets such as 401k, IRA, etc., to facilitate easy identification and usage in various parts of the application.
- **Details**: This enhancement will allow users to add custom labels to their assets, making it easier to identify and reference them in different scenarios and reports.
- **Implementation Steps**:
  1. Update the asset management interface to include an option for users to add labels to their assets.
  2. Ensure that these labels are stored and associated with the respective assets in the database.
  3. Modify relevant parts of the application to display these labels alongside asset information.
  4. Provide users with the ability to edit or remove labels as needed.

## 11. AI-Adjusted Roth Withdrawals for Social Security Loss

- **Objective**: Automatically adjust Roth IRA withdrawals to compensate for the loss of Social Security income and visualize the impact on Roth asset spend down.
- **Details**: This enhancement will use AI to dynamically adjust Roth IRA withdrawals when Social Security benefits are reduced or lost, ensuring users maintain their desired income level. A graph will display the adjusted withdrawals and the resulting spend down of the Roth asset over time.
- **Implementation Steps**:
  1. Develop an AI model to analyze the user's financial situation and determine optimal Roth withdrawal adjustments when Social Security income changes.
  2. Integrate the AI model with the existing income management system to automate withdrawal adjustments.
  3. Create a graph component to visualize the adjusted Roth withdrawals and the spend down trajectory of the Roth asset.
  4. Ensure the user interface provides clear insights into the financial impact of these adjustments, helping users make informed decisions. 