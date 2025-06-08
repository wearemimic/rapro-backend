# Enhancements

## 1. Update `start.sh` Script

- **Objective**: Modify the `start.sh` script to include a check for any running processes on a specified port before proceeding with the build.
- **Details**: This enhancement will help prevent port conflicts by ensuring that no other services are running on the required port before starting the build process. If a process is found running on the port, the script should prompt the user to stop the process or choose a different port.
- **Implementation Steps**:
  1. Add a function in `start.sh` to check for running processes on the specified port using a command like `lsof -i :<port>`.
  2. If a process is found, output a message to the user indicating the conflict and provide options to resolve it.
  3. Proceed with the build only if the port is free or after the user resolves the conflict.

## 2. Show Graph for Masset Income

- **Objective**: When adding income, if it is a masset like a 401k, display a graph showing the spend down based on criteria and the amount left at death.
- **Details**: This enhancement will provide a visual representation of how the masset is spent over time, helping users understand the financial trajectory and remaining balance at the end of life.
- **Implementation Steps**:
  1. Identify when the income source is a masset like a 401k during the income addition process.
  2. Calculate the spend down trajectory based on user-defined criteria.
  3. Display a graph under the income entry showing the spend down and the projected amount left at death. 