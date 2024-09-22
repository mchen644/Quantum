#!/usr/bin/env python
# coding: utf-8

# In[1]:


from GBS_utils import gbs_simulation, save_program_and_results


# In[2]:


n_modes = 4
squeezing_param = [1.0, 0.8, 1.2, 0.9]  # Different squeezing for each mode
cutoff_dim = 5
seed = 42

state_vector, prog = gbs_simulation(n_modes, squeezing_param, cutoff_dim, seed)

program_data = save_program_and_results(
    state_vector, prog, n_modes, squeezing_param, cutoff_dim
)


# In[3]:


program_data


# In[ ]:




