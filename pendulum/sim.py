from collections import defaultdict
import random
import numpy as np
import matplotlib.pyplot as plt
from pendulum.utils import array_to_kv
from multiprocessing.dummy import Pool
from datetime import datetime
import pandas as pd

class Simulation(object):
    '''The simulation class includes methods for simulating a pendulum(s)
    with its controller(s), (and some methods for processing pendulum data)
    '''
    def __init__(self, dt, t_final, force):
        '''New Simulation object

        Parameters
        ----------
        dt : :obj:float
            timestep in s.
        t_final : :obj:float
            run the simulation from 0s to `t_final`
        force : :obj:function
            a function which takes 1 argument, t, and returns
            a force in N based on t.
        '''
        self.dt = dt # time step
        self.t_final = t_final # end at or before this time
        self.force = force # forcing function
    
    def simulate(self, pendulum, controller, **kwargs):
        '''Simulate a pendulum/controller combination from t_0 to t_final.

        Parameters
        ----------
        pendulum : :obj:Pendulum
            pendulum object to simulate
        controller : :obj:Controller
            controller object to simulate

        Returns
        -------
        :obj:pd.DataFrame
            The simulation data.
        '''
        # unpack kwargs
        plot = kwargs.pop('plot', False)
        times = []
        t = 0
        state = pendulum.y_0
        datas = defaultdict(list)
        statelabels = ['x', 'xd', 't', 'td']
        setpoints = np.array([
            [0,0,0,0],
            [random.uniform(-1,-1), 0, 0, 0]
        ])
        while t <= self.t_final:
            times.append(t)
            t += self.dt

        if plot:
            plt.ion()
            fig = plt.figure()
            ax = fig.add_subplot(111)
            l1, = ax.plot(times, [0] * len(times), ls='-', label='x')
            l2, = ax.plot(times, [0] * len(times), ls='-', label='t')
            l3, = ax.plot(times, [0] * len(times), ls='--', label='u')
            h3 = ax.axhline(y=0, color='k', linestyle=':', label='x (setpoint)')
            # future estimates
            lines = [
                {   'linesobj' : l1,
                    'index' : 0,
                    'type'  : 'plot'},
                {   'linesobj' : l2,
                    'index' : 2,
                    'type'  : 'plot'},
                {   'linesobj' : l3,
                    'type'  : 'action',
                    'index' : None},
                {   'linesobj' : h3,
                    'index' : 0,
                    'type'  : 'hline'}
            ]
            ax.legend()
        
        for k, t in enumerate(times):
            data = {}
            force = self.force(t)
            data.update(array_to_kv('state', statelabels , state))
            if t < self.t_final/2:
                setpoint = setpoints[0]
            else:
                setpoint = setpoints[1]
            if plot:
                action, controller_data = controller.policy(state, t, self.dt, setpoint, plot=(fig, ax, lines))
            else:
                action, controller_data = controller.policy(state, t, self.dt, setpoint)
            
            data.update(array_to_kv('setpoint', statelabels, setpoint))
            data.update(controller_data)
            data[('energy','kinetic')], data[('energy', 'potential')], data['energy','total'] = pendulum.get_energy(state)
            data[('forces','forces')] = force
            data[('control action','control action')] = action
            force += action
            state, _ = pendulum.solve(self.dt, state, force)
            for k, v in data.items():
                datas[k].append(v)
        if plot:
            plt.ioff()
        return pd.DataFrame(datas, index=times)
    
    def simulate_multiple(self, pendulums, controllers, parallel=True):
        '''Simulate many pendulum/controller combinations.

        If you are using random variables to populate pendulums/controllers, 
        make sure that you deepcopy those objects, because some parameters may
        be shared internally.

        Parameters
        ----------
        pendulums : :obj:`list` of :obj:`Pendulum`
            the pendulums to simulate, in order
        controllers : :obj:`list` of :obj:`Controller`
            the controllers to simulate, in order. Must be same 
            length as pendulums.
        parallel : :obj:`bool`, optional
            whether to simulate in parallel, by default True. simulation
            is almost completely CPU bound so if you can use this, do.

        Returns
        -------
        :obj:pd.DataFrame
            MultiIndex DataFrame of simulations. Simulations are stacked on axis 0,
            so axis=0 level=0 contains the run # and axis=0 level=1 contains individual
            simulation data.

        Raises
        ------
        ValueError
            If pendulums/controllers are not equal length.
        '''
        if len(pendulums) != len(controllers):
            raise ValueError('pendulums and controllers must have same length. len(pendulums)={}, len(controllers)={}'.format(len(pendulums), len(controllers)))

        if parallel:
            pool = Pool(16)
            print('Simulating {} runs.'.format(len(pendulums)))
            tic = datetime.now()
            results = pool.starmap(self.simulate, zip(pendulums, controllers))
            toc = datetime.now()
            print('finished in {}'.format(toc - tic))
            return pd.concat(results, axis=0, keys=list(range(len(results))))
        else:
            print('Simulating {} runs.'.format(len(pendulums)))
            tic = datetime.now()
            allresults = []
            for pendulum, controller in zip(pendulums, controllers):
                results = self.simulate(pendulum, controller)
                allresults.append(results)
            toc = datetime.now()
            print('finished in {}'.format(toc - tic))
            return pd.concat(allresults, axis=0, keys = list(range(len(results))))