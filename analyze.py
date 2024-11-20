import pandas
import numpy
import matplotlib.pyplot as plt

#data sources
linux ='Data/newLinux.csv'
windows ='Data/newWindows.csv'

#columns in the data
#Linux Data Headers
##datatype measurement,dateTime:2006-01-02T15:04:05.000Z,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double
#LinuxPCM,DateTime,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,READ,WRITE,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,C0res%,C1res%,C3res%,C6res%,C7res%,C0res%,C2res%,C3res%,C6res%,C7res%,C8res%,C9res%,C10res%,Proc Energy (Joules),Power Plane 0 Energy (Joules),Power Plane 1 Energy (Joules),EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,READ,WRITE,IO,IA,GT,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,C0res%,C1res%,C3res%,C6res%,C7res%,C0res%,C2res%,C3res%,C6res%,C7res%,C8res%,C9res%,C10res%,SKT0,SKT0,SKT0,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,

#Windows Data Headers
##datatype measurement,dateTime:2006-01-02T15:04:05.000Z,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double
#WindowsPCM,DateTime,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,READ,WRITE,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,C0res%,C1res%,C3res%,C6res%,C7res%,C0res%,C2res%,C3res%,C6res%,C7res%,C8res%,C9res%,C10res%,Proc Energy (Joules),Power Plane 0 Energy (Joules),Power Plane 1 Energy (Joules),EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,READ,WRITE,IO,IA,GT,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,C0res%,C1res%,C3res%,C6res%,C7res%,C0res%,C2res%,C3res%,C6res%,C7res%,C8res%,C9res%,C10res%,SKT0,SKT0,SKT0,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,

#Load data
linux_data = pandas.read_csv(linux, skiprows=1)
windows_data = pandas.read_csv(windows, skiprows=1)

print(linux_data)
print(windows_data)

linux_data['DateTime'] = pandas.to_datetime(linux_data['DateTime'])
windows_data['DateTime'] = pandas.to_datetime(windows_data['DateTime'])

# Plot data
plt.figure(figsize=(10, 5))

# Plot Linux energy usage
plt.plot(linux_data['DateTime'], linux_data['Proc Energy (Joules)'], label='Linux Energy Usage')

# Plot Windows energy usage
plt.plot(windows_data['DateTime'], windows_data['Proc Energy (Joules)'], label='Windows Energy Usage')

# Add labels and title
plt.xlabel('DateTime')
plt.ylabel('Energy Usage (Joules)')
plt.title('Energy Usage over Time')
plt.legend()

# Show plot
plt.show()
