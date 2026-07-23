import numpy as np
import scipy.special as sp

def levy(n, m, beta):
    """
    Levy flight generation
    n: number of agents
    m: dimensions
    beta: power law exponent
    """
    num = sp.gamma(1 + beta) * np.sin(np.pi * beta / 2)
    den = sp.gamma((1 + beta) / 2) * beta * 2**((beta - 1) / 2)
    sigma_u = (num / den)**(1 / beta)
    
    u = np.random.normal(0, sigma_u, (n, m))
    v = np.random.normal(0, 1, (n, m))
    
    z = u / (np.abs(v)**(1 / beta))
    return z

class NOA:
    def __init__(self, fobj, dim, lb, ub, search_agents_no, max_iter):
        """
        Nutcracker Optimization Algorithm
        """
        self.fobj = fobj
        self.dim = dim
        self.lb = np.array(lb) # Lower bound array
        self.ub = np.array(ub) # Upper bound array
        self.search_agents_no = search_agents_no
        self.max_iter = max_iter
        
        self.alpha_param = 0.05
        self.Pa2 = 0.2
        self.Prb = 0.2

    def optimize(self):
        # Initialization
        positions = np.zeros((self.search_agents_no, self.dim))
        for i in range(self.dim):
             positions[:, i] = np.random.uniform(self.lb[i], self.ub[i], self.search_agents_no)
             
        lbest = positions.copy()
        lfit = np.full(self.search_agents_no, float('inf'))
        
        nc_fit = np.zeros(self.search_agents_no)
        
        best_nc = np.zeros(self.dim)
        best_score = float('inf')
        
        convergence_curve = []
        
        # Initial evaluation
        for i in range(self.search_agents_no):
            nc_fit[i] = self.fobj(positions[i, :])
            lfit[i] = nc_fit[i]
            
            if nc_fit[i] < best_score:
                best_score = nc_fit[i]
                best_nc = positions[i, :].copy()
                
        t = 0
        while t < self.max_iter:
            RL = 0.05 * levy(self.search_agents_no, self.dim, 1.5)
            l_param = np.random.rand() * (1 - t / self.max_iter)
            
            if np.random.rand() < np.random.rand():
                a = (t / self.max_iter)**(2 * 1 / (t + 1e-10)) # Avoid div by zero
            else:
                a = (1 - (t / self.max_iter))**(2 * (t / self.max_iter))
                
            # Logic branch 1 (Main Foraging) or 2 (Cache/Recovery)
            # Note: The MATLAB code structure is a bit convoluted with "if rand<rand" logic that wraps the loop.
            # I will implement the logic as interpreted from the MATLAB flow.
            
            # The MATLAB code loops agents inside the "if rand<rand" which is odd - it likely means "For this generation, decide strategy".
            # BUT typical optimization algos decide per agent. Let's look closely at MATLAB code:
            # "if rand<rand % Foraging" -> This block contains a loop "for i=1:SearchAgents_no".
            # So the STRATEGY is chosen for the WHOLE POPULATION for that iteration step in the outer block?
            # Yes, "if rand<rand" is OUTSIDE the "for i=1:SearchAgents_no".
            
            strategy_choice = np.random.rand() < np.random.rand()
            
            if strategy_choice: # Foraging and storage strategy
                mo = np.mean(positions, axis=0)
                
                for i in range(self.search_agents_no):
                    # Update mu
                    r_mu = np.random.rand()
                    if r_mu < np.random.rand():
                        mu = np.random.rand()
                    elif np.random.rand() < np.random.rand():
                        mu = np.random.randn()
                    else:
                        mu = RL[0, 0] # Simplified from RL(1,1)
                    
                    cv = np.random.randint(0, self.search_agents_no)
                    cv1 = np.random.randint(0, self.search_agents_no)
                    
                    Pa1 = (self.max_iter - t) / self.max_iter
                    
                    if np.random.rand() < Pa1: # Exploration phase 1
                        cv2 = np.random.randint(0, self.search_agents_no)
                        r2 = np.random.rand()
                        for j in range(self.dim):
                            if t < self.max_iter / 2:
                                if np.random.rand() > np.random.rand():
                                    term3 = mu * (1 if np.random.rand()<0.5 else 0) * (r2*r2*self.ub[j] - self.lb[j]) # Approximation of (rand<5)? likely (rand<0.5) typo in matlab or always true if 5
                                    # Matlab: (rand<5) is always 1 (true). So it's just mu * ...
                                    positions[i, j] = mo[j] + RL[i, j] * (positions[cv, j] - positions[cv1, j]) + mu * (r2*r2*self.ub[j] - self.lb[j])
                            else:
                                if np.random.rand() > np.random.rand():
                                    positions[i, j] = positions[cv2, j] + mu * (positions[cv, j] - positions[cv1, j]) + mu * (1 if np.random.rand() < self.alpha_param else 0) * (r2*r2*self.ub[j] - self.lb[j])
                    else: # Exploitation phase 1
                         mu = np.random.rand()
                         if np.random.rand() < np.random.rand():
                             r1 = np.random.rand()
                             for j in range(self.dim):
                                 positions[i, j] = positions[i, j] + mu * abs(RL[i, j]) * (best_nc[j] - positions[i, j]) + r1 * (positions[cv, j] - positions[cv1, j])
                         elif np.random.rand() < np.random.rand():
                             for j in range(self.dim):
                                 if np.random.rand() > np.random.rand():
                                     positions[i, j] = best_nc[j] + mu * (positions[cv, j] - positions[cv1, j])
                         else:
                             for j in range(self.dim):
                                 positions[i, j] = best_nc[j] * abs(l_param)

            else: # Cache-search and Recovery strategy
                 RP = np.zeros((2, self.dim))
                 for i in range(self.search_agents_no):
                     # Construct Reference Points RP
                     ang = np.pi * np.random.rand()
                     cv = np.random.randint(0, self.search_agents_no)
                     cv1 = np.random.randint(0, self.search_agents_no)
                     
                     # Pythonic way to doing the RP calculation loop
                     for j in range(self.dim):
                         # RP1
                         if ang != np.pi/2:
                             RP[0, j] = positions[i, j] + (a * np.cos(ang) * (positions[cv, j] - positions[cv1, j]))
                         else:
                             RP[0, j] = positions[i, j] + a * np.cos(ang) * (positions[cv, j] - positions[cv1, j]) + a * RP[np.random.randint(0,2), j]
                         
                         # RP2
                         term_rand = (self.ub[j]-self.lb[j])*np.random.rand() + self.lb[j]
                         
                         if ang != np.pi/2:
                             RP[1, j] = positions[i, j] + (a * np.cos(ang) * ((self.ub[j]-self.lb[j]) + self.lb[j])) * (1 if np.random.rand() < self.Prb else 0)
                         else:
                             RP[1, j] = positions[i, j] + (a * np.cos(ang) * term_rand + a * RP[np.random.randint(0,2), j]) * (1 if np.random.rand() < self.Prb else 0)

                     # Boundary check for RP
                     # (Simplified based on MATLAB logic)
                     
                     # Recovery Stage or Cache Search
                     if np.random.rand() < self.Pa2: # Recovery
                         cv = np.random.randint(0, self.search_agents_no)
                         if np.random.rand() < np.random.rand():
                             for j in range(self.dim):
                                 if np.random.rand() > np.random.rand():
                                     positions[i, j] = positions[i, j] + np.random.rand()*(best_nc[j] - positions[i, j]) + np.random.rand()*(RP[0, j] - positions[cv, j])
                         else:
                             for j in range(self.dim):
                                 if np.random.rand() > np.random.rand():
                                     positions[i, j] = positions[i, j] + np.random.rand()*(best_nc[j] - positions[i, j]) + np.random.rand()*(RP[1, j] - positions[cv, j])
                     else: # Cache-search
                         pass # The MATLAB code just did evaluation here? Yes.
                         
            # Clip Bounds
            for i in range(self.search_agents_no):
                for j in range(self.dim):
                    positions[i, j] = np.clip(positions[i, j], self.lb[j], self.ub[j])

            # Evaluation Loop (Common for both branches effectively)
            # In MATLAB, evaluation was inside the loop. Here we can do it after position updates.
            for i in range(self.search_agents_no):
                fitness = self.fobj(positions[i, :])
                
                if fitness < lfit[i]:
                    lfit[i] = fitness
                    lbest[i, :] = positions[i, :].copy()
                
                if fitness < best_score:
                    best_score = fitness
                    best_nc = positions[i, :].copy()
            
            t += 1
            if t > self.max_iter: break
            convergence_curve.append(best_score)
            print(f"Iteration {t}/{self.max_iter}, Best Fitness: {best_score}")

        return best_score, best_nc, convergence_curve
