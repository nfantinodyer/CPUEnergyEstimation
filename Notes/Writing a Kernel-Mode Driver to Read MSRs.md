#CSEN283

---
### **Safety Precautions**

- **Testing Environment:** Use a virtual machine or a separate test system to prevent system crashes affecting your main development machine.
- **Backup Plan:** Regularly backup your work and have recovery options ready.

---

## **Week-by-Week Plan**

### **Week 1: Research and Planning**

#### **Day 1-2: Understanding MSRs and RAPL**

- **Read Intel's Documentation:**
    - **Intel® 64 and IA-32 Architectures Software Developer's Manual**, Volume 3.
    - Focus on sections related to RAPL and energy consumption MSRs.
- **Identify Relevant MSRs:**
    - `MSR_PKG_ENERGY_STATUS` (0x611): Total energy consumed by the processor package.
    - Other MSRs for cores or other components if necessary.

#### **Day 3-4: Windows Kernel Development Basics**

- **Study Windows Driver Development:**
    - Learn about Windows Driver Model (WDM) and Kernel-Mode Driver Framework (KMDF).
    - Read tutorials on writing basic kernel drivers.
- **Set Up Development Environment:**
    - Install **Windows Driver Kit (WDK)** and **Visual Studio**.
    - Configure a test machine or virtual machine for driver deployment.

#### **Day 5-7: Planning the Driver Architecture**

- **Define Driver Functionality:**
    - The driver will read specified MSRs and provide the data to user-space applications.
    - Implement an IOCTL interface for communication.
- **Create Project Structure:**
    - Set up the initial driver project in Visual Studio.
    - Plan for future expansion if time permits.

---

### **Week 2: Developing the Kernel-Mode Driver**

#### **Day 8-10: Writing the Driver Code**

- **Implement Driver Entry Points:**
    - `DriverEntry`: The main entry point for the driver.
    - `EvtDriverDeviceAdd`: Called when the driver is loaded.
- **Set Up Device and Symbolic Links:**
    - Create a device object and symbolic link for user-space communication.

#### **Day 11-14: Implementing MSR Access**

- **Reading MSRs:**
    - Use the intrinsic function `_readmsr` in C.
        `#include <intrin.h> ULONGLONG msr_value = __readmsr(MSR_PKG_ENERGY_STATUS);`
    - Ensure the driver runs at the appropriate IRQL (Interrupt Request Level).
- **Handle IOCTLs:**
    - Define IOCTL codes using `CTL_CODE` macro.
    - Implement `EvtDeviceIoControl` to handle IOCTL requests.

---

### **Week 3: Testing and Refinement**

#### **Day 15-17: Testing the Driver**

- **Build and Sign the Driver:**
    
    - Compile the driver and sign it for test deployment.
- **Deploy to Test Environment:**
    
    - Install the driver on the test machine.
    - Use **Driver Verifier** to catch common errors.
- **Debugging:**
    
    - Use **WinDbg** for kernel debugging.
    - Set breakpoints and monitor driver behavior.

#### **Day 18-21: Ensuring Stability and Security**

- **Handle Edge Cases:**
    
    - Ensure the driver correctly handles invalid IOCTL requests.
    - Prevent unauthorized access by implementing proper access control.
- **Documentation:**
    
    - Comment code thoroughly.
    - Keep a log of changes and testing results.

---

### **Week 4: Developing the User-Space Application**

#### **Day 22-24: Creating the Communication Interface**

- **Open a Handle to the Driver:**
    
    - Use `CreateFile` in user-space to communicate with the driver.
        
        csharp
        
        Copy code
        
        `IntPtr hDevice = CreateFile("\\\\.\\MsrDriver", ...);`
        
- **Sending IOCTL Requests:**
    
    - Use `DeviceIoControl` to send requests and receive data.

#### **Day 25-28: Collecting and Interpreting Data**

- **Reading Energy Data:**
    
    - Receive raw MSR values from the driver.
    - Convert the raw values to energy readings using Intel's documented formulas.
        - Energy units can be calculated from `MSR_RAPL_POWER_UNIT`.
- **Process-Level CPU Usage:**
    
    - Use `Pdh` (Performance Data Helper) or `GetProcessTimes` to get CPU usage per process.
    - Collect data over time intervals for correlation.

---

### **Week 5: Correlating Data and Visualization**

#### **Day 29-31: Estimating Per-Process Energy Consumption**

- **Correlation Algorithm:**
    
    - Calculate the proportion of total CPU time used by each process.
    - Estimate each process's energy consumption based on its CPU usage percentage.
- **Example Calculation:**
    
    `ProcessEnergy = TotalEnergyConsumed * (ProcessCPUTime / TotalCPUTime)`
    

#### **Day 32-33: Implementing Visualization**

- **Develop a Simple GUI:**
    
    - Use a lightweight GUI framework (e.g., WinForms, WPF).
    - Display real-time graphs showing energy consumption per process.
- **User Interaction:**
    
    - Allow users to select processes and view detailed statistics.