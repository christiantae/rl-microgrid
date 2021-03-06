# Kevin Moy, 7/24/2020
# Modified from an example in the OpenDSS Python documentation
# Sandbox file to test and demonstrate OpenDSS Python COM interface
# Uses IEEE 13-bus system to scale loads, demonstrate voltage change when loads are disconnected

import win32com.client
from generate_state_space import load_states

# ****************************************************
# * Initialize OpenDSS
# ****************************************************
# Instantiate the OpenDSS Object
try:
    DSSObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
except:
    print("Unable to start the OpenDSS Engine")
    raise SystemExit
# Set up the Text, Circuit, and Solution Interfaces
DSSText = DSSObj.Text
DSSCircuit = DSSObj.ActiveCircuit
DSSSolution = DSSCircuit.Solution

# Load in an example circuit
DSSText.Command = r"Compile 'C:\Program Files\OpenDSS\IEEETestCases\13Bus\IEEE13Nodeckt.dss'"

# Get tuple of all loads and their buses
loadbus = []
loadNames = DSSCircuit.Loads.AllNames
# Or array for literally each connection between bus terminal and load:
for load in loadNames:
    DSSCircuit.SetActiveElement("Load." + load)
    # Get bus of load
    bus = DSSCircuit.ActiveDSSElement.Properties("bus1").Val
    loadbus.append([load, bus])

# Get array of all capacitors and their buses
capbus = []
capNames = DSSCircuit.Capacitors.AllNames
# Or array for literally each connection between bus terminal and load:
for cap in capNames:
    DSSCircuit.SetActiveElement("Capacitor." + cap)
    # Get bus of load
    bus = DSSCircuit.ActiveDSSElement.Properties("bus1").Val
    capbus.append([cap, bus])

# Etc. etc. for other elements (switches, generators, transformers, etc.)
# Disable voltage regulators
DSSText.Command = "Disable regcontrol.Reg1"
DSSText.Command = "Disable regcontrol.Reg2"
DSSText.Command = "Disable regcontrol.Reg3"

loadKws = None
while loadKws is None:
    loadKws = load_states(loadNames, DSSCircuit, DSSSolution)

print(loadKws)

# ----- Model effects of altering a load 30 seconds into a simulation -----

# Configure monitor
DSSText.Command = "New Monitor.Mon1 element=Line.692675 mode=0"
DSSSolution.StepSize = 1  # Set step size to 1 sec
DSSSolution.Number = 30  # Solve 30 seconds of the simulation

# Set the solution mode to duty cycle, forcing loads to use their "duty cycle" loadshape, allowing time based simulation
DSSSolution.Mode = 6  # Code for duty cycle mode
# DSSText.Command = "Set Mode=Dutycycle" # More readable than above

# Solve for initial condition (first 30 seconds)
DSSSolution.Solve()

# Increase load at bus 671 to set kW
DSSCircuit.SetActiveElement("Load.671")
DSSCircuit.ActiveDSSElement.Properties("kW").Val = 2000  # try changing to 1000, 3000
# # Disconnect load at bus 671 from circuit
# DSSText.Command = "Open Load.671"  # not sure why this doesn't work with ' DSSCircuit.Disable("Load.671") ' ?
# # Alternatively: Open line between bus 692 and bus 675
# DSSText.Command = "Open Line.684611"

# Activate capacitor bank at bus 675 (cap1)
# Set a capacitor's rated kVAR to 1200
DSSCircuit.SetActiveElement("Capacitor.Cap1")
DSSCircuit.ActiveDSSElement.Properties("kVAR").Val = 1500  # try changing to 1500, 2000
DSSCircuit.Enable("Cap1")

# Solve another 30 seconds of simulation
DSSSolution.Number = 30
DSSSolution.Solve()
if DSSSolution.Converged:
    print("The Circuit Solved Successfully")
else:
    print("The Circuit Did Not Solve Successfully")
print("Seconds Elapsed: " + str(DSSSolution.Seconds))

# Plot the voltage for the 60 seconds of simulation
DSSText.Command = "Plot monitor object=Mon1 Channels=(1,3,5)"  # Line voltage should increase, as expected

# ----- PLOTTING ----- #
# From IEEE123 test case in OpenDSS, "CircuitPlottingScripts.dss"
# These settings make a more interesting voltage plot since the voltages are generally OK for this case
# Voltages above     1.02            will be BLUE
# Voltages between   0.97 and 1.02   will be GREEN
# Voltages below     0.97            will be RED
# These are the default colors for the voltage plot
DSSText.Command = "Set normvminpu=1.05"
DSSText.Command = "Set emergvminpu=0.95"

# # Mark transformers, switches, and capacitors
DSSText.Command = "Set markTransformers=yes"
DSSText.Command = "Set Transmarkersize=3"
DSSText.Command = "Set markSwitches=yes"
DSSText.Command = "Set markCapacitors=yes"
DSSText.Command = "Set Capmarkersize=3"

# Plot!
DSSText.Command = "Plot circuit voltage dots=y labels=y"

# ----- EXPORTING RESULTS ----- #
# Export voltage to a csv file in a particular directory
DSSText.Command = r"Set datapath = 'C:\Users\kmoy1\PycharmProjects\smart-rl-mg'"  # Set to your own filepath!
DSSText.Command = "Export Voltages"
Filename = DSSText.Result
print("File saved to: " + Filename)

VoltageMags = DSSCircuit.AllBusVmagPu
# print(VoltageMags)
