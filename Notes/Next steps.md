#CSEN283 
Establish Regression Models: Use linear regression or other curve-fitting techniques to create estimation formulas based on your PCM data. For example, you might model power as a function of CPU utilization and core count.

To generate CPU workloads similar to those an OS would create:
    •    Simulate Workloads: Use software like stress-ng, which allows you to create synthetic workloads that stress various CPU components and subsystems. You can control the intensity and duration of these tasks, simulating OS-level tasks like file I/O, computations, and more.

### Use
[[stress-ng]]
[[cpufreq-set]] 
-> windows equivalent is 
**Intel Extreme Tuning Utility (XTU):**
- Designed for Intel CPUs to adjust performance settings.
- **Download:** Intel XTU

### Estimation Models

#### Existing Models
##### Utilization Model
Power_CPU = P_idle + (P_max - P_idle) * CPU_utilization
- **P_idle:** Power when the CPU is idle.
- **P_max:** Power at maximum CPU utilization.
- **CPU_utilization:** Current CPU usage (0 to 1).
##### Performance Model
Power_CPU = α * IPC + β * Cache_Misses + γ
Use hardware performance counters (e.g., instructions retired, cache misses) to estimate power.
-  **IPC:** Instructions per cycle.
- **Cache_Misses:** Number of cache misses.
- **α, β, γ:** Model coefficients determined through regression analysis.
##### Frequency and Voltage Scaling Models
Power_CPU = V^2 * F
- **V:** CPU voltage.
- **F:** CPU frequency.

#### My Own
Estimated_Power = α + (β1 * CPU_Utilization) + (β2 * CPU_Frequency) + (β3 * IPC) + (β4 * L3MPI) + (β5 * Temperature)

Linux:
Estimated Power (Joules) = 0.5893
                           - 0.0124 * CPU Utilization
                           + 3.6398 * FREQ
                           + 0.0682 * IPC
                           - 3.5541 * L3MPI
                           - 0.0055 * TEMP

Windows:
Estimated Power (Joules) = 0.5537
                           - 0.0623 * CPU Utilization
                           + 8.1627 * FREQ
                           + 0.0238 * IPC
                           + 49.2031 * L3MPI
                           + 0.0013 * TEMP

### **Understanding the Coefficients**

#### **1. Intercept (`const`)**

- **Interpretation:**
    - Represents the estimated energy consumption when all independent variables are zero.
    - It serves as the baseline level of energy consumption in your model.

#### **2. Coefficients of Independent Variables**

- **Each Coefficient Represents:**
    - The estimated change in the dependent variable (energy consumption) for a one-unit increase in the predictor variable, holding all other variables constant.

#### **3. Specific Coefficients Explained**

##### **Linux Model:**

- **`CPU Utilization`: -0.0124**
    
    - **Interpretation:**
        - For every 1% increase in CPU Utilization, the estimated energy consumption decreases by approximately 0.0124 Joules, holding other variables constant.
    - **Note:**
        - A negative coefficient might seem counterintuitive; it could be due to multicollinearity or other underlying factors in the data.
- **`FREQ`: +3.6398**
    
    - **Interpretation:**
        - For every 1 GHz increase in frequency, the estimated energy consumption increases by approximately 3.6398 Joules.
- **`IPC`: +0.0682**
    
    - **Interpretation:**
        - For every unit increase in Instructions Per Cycle, energy consumption increases by approximately 0.0682 Joules.
- **`L3MPI`: -3.5541**
    
    - **Interpretation:**
        - For every unit increase in L3 Cache Misses Per Instruction, energy consumption decreases by approximately 3.5541 Joules.
    - **Note:**
        - This negative relationship might be due to less energy being used when the processor stalls on cache misses.
- **`TEMP`: -0.0055**
    
    - **Interpretation:**
        - For every 1-degree Celsius increase in temperature, energy consumption decreases by approximately 0.0055 Joules.

##### **Windows Model:**

- **`CPU Utilization`: -0.0623**
    
    - **Interpretation:**
        - For every 1% increase in CPU Utilization, the estimated energy consumption decreases by approximately 0.0623 Joules.
- **`FREQ`: +8.1627**
    
    - **Interpretation:**
        - For every 1 GHz increase in frequency, the estimated energy consumption increases by approximately 8.1627 Joules.
- **`IPC`: +0.0238**
    
    - **Interpretation:**
        - For every unit increase in Instructions Per Cycle, energy consumption increases by approximately 0.0238 Joules.
- **`L3MPI`: +49.2031**
    
    - **Interpretation:**
        - For every unit increase in L3 Cache Misses Per Instruction, energy consumption increases by approximately 49.2031 Joules.
    - **Note:**
        - A positive coefficient here suggests that more cache misses lead to higher energy consumption, which makes intuitive sense.
- **`TEMP`: +0.0013**
    
    - **Interpretation:**
        - For every 1-degree Celsius increase in temperature, energy consumption increases by approximately 0.0013 Joules.