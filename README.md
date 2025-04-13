# CS4348 Project 2 - Bank Simulation

## Overview
This project simulates a bank using Python threads and semaphores. There are:
- 3 tellers
- 50 customers

Customers enter the bank, get in line, and perform deposit or withdrawal transactions with available tellers. Tellers interact with a shared manager and safe. Proper synchronization ensures that:
- Only 2 tellers can be in the safe at once
- Only 1 teller can interact with the manager at a time
- Only 2 customers can enter the bank at once

## Files
- `bank_simulation.py`: Main Python script implementing the bank simulation
- `devlog-#.md`: Session logs detailing the development process
- `README.md`: This file

## How to Run
1. Ensure you have **Python 3** installed.
2. Open a terminal in the project directory.
3. Run the simulation with:
```bash
python3 bank_simulation.py
```

The output will log each teller and customer action as per the required format.

## Notes for the TA
- Synchronization is implemented using Python's `threading.Semaphore` and `threading.Event`.
- Tellers and customers interact through semaphores for request/response.
- The output simulates a realistic bank workflow and matches the example provided.
- All logs are printed to standard output for evaluation.

Enjoy the simulation!
