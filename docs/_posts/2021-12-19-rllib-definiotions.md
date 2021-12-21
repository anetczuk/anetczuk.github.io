---
title: RLlib basic definitions and concepts

summary: Explanation of basic definitions related to RLlib and reinforcement learning in general with references to RLlib configuration parameters.
---


RLlib allows to configure execution of it's algorithms using plenty of configuration parameters. Those parameres can be difficult to understand at first glance. Following dictionary might be helpful for novice users to start with RL and RLlib.  

- *environment* -- world where training and evaluation of agent take place.

- *task* -- exercises to execute and goals to achieve on given environment. Task is *episodic* when it has termination state (e.g. *MountainCar* problem), otherwise is describred as *continuous* (e.g. *Pendulum* problem). Continuous tasks are usually limited by `train_batch_size` config variable.

- *episode* -- single execution of task from it's beginning to end.

- *rollout* -- sequence of state and action. During training, length of rollout is controlled by `batch_mode` and `rollout_fragment_length`. 

- *epoch* -- one propagation and update of weights through neural network. In broader context can be treated as single iteration of training or evaluation phase.

- *timestep* -- single step executed on environment. Multiple timesteps make up the episode.

- *training* -- execution of single epoch with learning phase.

- *evaluation* -- execution of single epoch without learning phase.

- *metrics* -- agregated values describing quality of training phase. Basic result metrics are `episode_reward_max`, `episode_reward_mean` and `episode_reward_min`. Number of *metrics* samples is controlled by `metrics_num_episodes_for_smoothing` variable. Value '1' means not to perform aggregation of rewards from previous traininig iterations.

- *learning rate* -- basic parameter of learning algorithms. Can be configured by `lr` parameter.

- *bootstraping* -- updating (learning) value based on estimation rather than on exact value

<br/>
Based on RLlib/Ray version 1.9.0


### References

- RLlib documentation ([https://docs.ray.io/en/latest/rllib](https://docs.ray.io/en/latest/rllib))