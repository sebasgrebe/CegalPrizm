# Start: PWR Description

from cegalprizm.scripting_server import WorkflowDescription

pwr_description = WorkflowDescription(name="Smooth log",
                                      category="Well",
                                      description="This workflow creates a smoothed log",
                                      authors="user@company.com",
                                      version="0.1")

pwr_description.add_object_ref_parameter("well_id", "Well", "A borehole", "well")
pwr_description.add_object_ref_parameter("log_id", "Log", "The global well log to be smoothed", "global_continuous_log")
pwr_description.add_integer_parameter("window_length", "Window Length", "The window length to be used when smoothing", 80, 2, 500)
pwr_description.add_string_parameter("suffix", "Suffix", "The suffix to be appended to the name of the smoothed log", "smooth")

if 'parameters' not in locals() and 'parameters' not in globals():
    parameters = pwr_description.get_default_parameters()

# End: PWR Description

from cegalprizm.pythontool import PetrelConnection

ptp = PetrelConnection()

petrel_objects = ptp.get_petrelobjects_by_guids([parameters['well_id'], parameters['log_id']])

well = petrel_objects[0]
cont_log = petrel_objects[1].log(well.petrel_name)

logs_df = well.logs_dataframe(cont_log)

logs_df = logs_df.set_index('MD')
logs_df = logs_df[cont_log.petrel_name]

smooth_logs_df = logs_df.rolling(parameters['window_length'], win_type='gaussian', center=True).mean(std=20)

new_sm_log = cont_log.clone(f'{cont_log.petrel_name}_{parameters["suffix"]}')  # create the clone if it doesn't already exist

# get columns of smooth_logs_df DataFrame and convert to NumPy ndarrays
md = smooth_logs_df.index.to_numpy()
new_sm_values = smooth_logs_df.to_numpy()
new_sm_log.set_values(md, new_sm_values)
