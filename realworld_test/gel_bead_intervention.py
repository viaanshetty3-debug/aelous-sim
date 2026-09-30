"""Polycrylate gel bead injection intervention."""

import numpy as np


class GelBeadIntervention:
    def __init__(self, world, bead_strength=0.3, injection_radius_m=200.0, start_step=20):
        self.world = world
        self.strength = bead_strength
        self.inj_r = injection_radius_m
        self.start_step = start_step
        # Create mask for core region using actual R grid
        self.core_mask = world.R < injection_radius_m
    
    def forcings(self, step):
        S_u = np.zeros_like(self.world.u)
        S_v = np.zeros_like(self.world.v)
        S_w = np.zeros_like(self.world.w)
        S_b = np.zeros_like(self.world.b)
        
        if step < self.start_step:
            return {"S_u": S_u, "S_v": S_v, "S_w": S_w, "S_b": S_b}
        
        # Apply quadratic drag in core
        S_u[self.core_mask] -= self.strength * np.abs(self.world.u[self.core_mask]) * self.world.u[self.core_mask]
        S_v[self.core_mask] -= self.strength * np.abs(self.world.v[self.core_mask]) * self.world.v[self.core_mask]
        S_w[self.core_mask] -= self.strength * np.abs(self.world.w[self.core_mask]) * self.world.w[self.core_mask]
        
        return {"S_u": S_u, "S_v": S_v, "S_w": S_w, "S_b": S_b}
