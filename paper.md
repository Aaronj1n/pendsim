---
title: 'pendsim: Developing, Simulating, and Visualizing Feedback Controlled Inverted Pendulum Dynamics'
tags:
  - Python
  - control theory
  - dynamics
  - control
  - engineering simulation
authors:

  - name: Mike Sutherland
    orcid: 0000-0001-5394-2737
    affiliation: 1

  - name: David A. Copp
    orcid: 0000-0002-5206-5223
    affiliation: 1

affiliations:
  - name: Department of Mechanical and Aerospace Engineering, University of California, Irvine
    index: 1

date: 10 Nov 2021
bibliography: paper.bib
---

# Summary

This package is a companion tool for exploring dynamics, control, and machine
learning for the canonical cart-and-pendulum system. It includes a software
simulation of the cart-and-pendulum system, a visualizer tool to create
animations of the simulated system, and sample implementations for controllers
and state estimators. The user can use any platform or the browser to
run the `pendsim` Python package. It gives the user a plug-and-play sandbox
to design and analyze controllers for the inverted pendulum, and is compatible
with Python's rich landscape of third-party scientific programming and machine
learning libraries.

The package is useful for a wide range of curricula, from introductory
mechanics to graduate-level control theory. The inverted pendulum is a
canonical example in control theory (See, e.g. [@Astrom:2008]). A set of
example notebooks provide a starting point for introductory and
graduate-level topics.

# Statement of need

Curricula in the study of dynamical systems and control can be quite
abstract. When a student studies the abstract mathematical model of a system they
have difficulty seeing the effects of control and modeling parameters.
Because of this, direct experimentation is a natural way to better
understand how these systems evolve over time given different
controllers and parameters.

Physical laboratory setups are expensive, time-consuming, and limited to
four or five students at a time. Virtual experiments are cheap,
easy-to-setup, and accomodate hundreds of students at a time.  Virtual
experiments can augment course content, even for remote-only
instruction.  The virtual platform allows students to share their
work, run experiments collaboratively or individually, and develop
controllers or investigate system dynamics in a fast design-test loop. 

Instructors can design experiments in `pendsim`, and subsequently
measure any system parameter or variable, including the animation of the
system. The package includes visualizations and pre-built controllers.
The package is a great companion to any control or dynamical systems course
material, in either a virtual, hybrid, or in-person context. 


# Example Usage

The software is a virtual laboratory. Users create an experiment by
specifying a set of parameters: the pendulum (mass, length, friction,
and so on), and the simulation parameters (such as external forces). The
user can then design and apply a control policy in the simulation.
Finally, the user can view the results of the simulation. The ability to
rapidly create and run experiments allows for fast design-test loops.

This design-test-visualize sequence also allows instructors to introduce 
students to new topics and create interactive assignments that can augment 
theoretical class discussions and hardware experiments. Thus, `pendsim` 
may be naturally used in engineering courses related to dynamics and control 
that are taught in any format, including in-person, hybrid, and online settings. 

The following simple example (Example 1) shows the ease of creating, modeling,
and visualizing a proportional-integral-derivative controller:

```python
### Example 1
# define simulation parameters
dt, t_final = 0.01, 5.0
def forcing_func(t):
    return 10 * np.exp(-(((t - 2.0) / 0.2) ** 2))

# define pendulum parameters
pend = sim.Pendulum(
    2.0,  # Large mass, 2.0 kg
    1.0,  # Small mass, 1.0 kg
    2.0,  # length of arm, 2.0 meter
    # state inputs are stored as numpy arrays:
    # [x, xdot, theta, thetadot]
    initial_state=np.array([0.0, 0.0, 0.1, 0.0]),
)

# PID gains
kp, ki, kd = 50.0, 0.0, 5.0
# controllers are stored in the controller module.
cont = controller.PID((kp, ki, kd))

# create simulation object
simu = sim.Simulation(
    # timestep, simulation time, and forcing function
    dt, t_final, forcing_func, 
    # simulate gaussian noise added to state measurements
    noise_scale=np.array([0.05, 0.05, 0.05, 0.05])
)

# run simulation with controller and pendulum objects
results = simu.simulate(pend, cont)

# create an animation of the results
visu = viz.Visualizer(results, pend)
ani = visu.animate()
```

![A still from the animation module. Here, a force pushes to the right
(shown in red) while the controller pushes to the left to stabilize the
pendulum (shown in
blue).\label{fig:example1}](forces_pend_anim_still.png)

Rich plots of any system attribute are easy to generate. This example
shows the plot in \autoref{fig:example2}:

```python
### Example 2
import matplotlib.pyplot as plt
fig, ax = plt.subplots()

ax.plot(results[("state", "t")])
ax.scatter(
  results.index, results[("measured state", "t")].values,
  color="black", marker=".",
  )
ax.set_ylabel("Angle (Radians)")
ax.set_xlabel("Time (s)")
ax.set_title("Pendulum Angle")
plt.show()
```
![This plot (generated by the code in Example 2) shows the angle of the
pendulum over time as it evolves in simulation. The black dots show the
measured angle, while the line shows an Unscented Kalman Filter
estimation of the angle.  Such plots are easy to generate from outputs
of the simulation.\label{fig:example2}](paper_angle_plot.png){ width=60%
}

# Package Features

## A core pendulum/simulation module. (`sim.py`)

This simulates the system dynamics and allows for external forces on the pendulum. Users can specify:

-   pendulum parameters (e.g., masses, length, friction, etc.)

-   a time period over which to simulate

-   an external forcing function (e.g., push)

-   noise characteristics

-   a timestep for the simulation

-   a controller to use, if any

## Controllers, Estimators, etc. (`controller.py`)

Several controller implementations are pre-built. These include:

-   Bang Bang (On-Off) controller

-   Proportional-Integral-Derivative (PID) controller

-   Linear Quadratic Regulator (LQR) controller

-   State estimation using an Unscented Kalman Filter (UKF) (implemented with package `filterpy` [@Labbe:2021] )

-   Energy Swing-Up Controller

The user can implement any control policy by creating a new class
[??link to
docs??](https://github.com/openjournals/jose-reviews/issues/168). Users
can test new open-ended controller designs.  Controllers can dump data
into the simulation results so that intermediate control inputs are
accessible to the final results of the simulation.

## Visualization (`viz.py`):


The simulation results are visualized in `viz.py`. The 'matplotlib'
[@Hunter:2007] backend draws animations of the inverted
pendulum and plots from the simulation. The visualization uses the
results of the simulation to draw the inverted pendulum, including the
external and control forces applied to it. The animation module allows
for the system to plot real-time simulation data (e.g., data used by the
controller) side by side with the animation.

The results of the simulation are easy to query and plot. This makes
investigating the simulation easy and intuitive.

## Example Notebooks:

The repository includes several notebooks which show the capabilities of
the package. Example notebooks are hosted on Google Colab:

-   [Animated Plots](https://colab.research.google.com/github/rland93/pendsim/blob/master/notebooks/tutorial_plot_inline.ipynb)

-   [System Linearization](https://colab.research.google.com/github/rland93/pendsim/blob/master/notebooks/linearization.ipynb)

-   [PID Tuning](https://colab.research.google.com/github/rland93/pendsim/blob/master/notebooks/PID.ipynb)

-   [PID Controller Design Assignment](https://colab.research.google.com/github/EASEL-UCI/pendsim/blob/main/notebooks/PID_controller_design_assignment.ipynb)

-   [Applying a state estimator for better control](https://colab.research.google.com/github/rland93/pendsim/blob/master/notebooks/state_estimation.ipynb)

-   [Swing-up by Energy Control](https://colab.research.google.com/github/rland93/pendsim/blob/master/notebooks/swingup.ipynb)
