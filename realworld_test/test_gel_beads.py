"""Quick test of gel bead intervention."""

from tornado_world import TornadoWorld, SCENARIOS
from aeolus_adapter import AeolusInterventionAdapter
from gel_bead_intervention import GelBeadIntervention


def test_gel_beads():
    scenario = SCENARIOS[1]  # Moore/EF5
    
    # Baseline (no intervention)
    world_base = TornadoWorld(scenario, seed=42, nr=50, nz=35)
    
    # Optimal intervention
    world_opt = TornadoWorld(scenario, seed=42, nr=50, nz=35)
    adapter_opt = AeolusInterventionAdapter(
        world_opt, use_thermal=True, use_momentum=True,
        thermal_peak_K=4.0, momentum_pressure_deficit_Pa=-500.0,
        start_step=20
    )
    
    # Gel beads
    world_gel = TornadoWorld(scenario, seed=42, nr=50, nz=35)
    gel_intervention = GelBeadIntervention(world_gel, start_step=20)
    
    print("=" * 70)
    print("COMPARING INTERVENTIONS: Optimal vs Gel Beads")
    print("=" * 70)
    print(f"Scenario: {scenario.name} | Peak v_t: {scenario.peak_vt_target:.1f} m/s\n")
    
    for step in range(200):
        # Baseline
        world_base.step(intervention_forcings=None)
        m_base = world_base.diagnose_metrics(t=step * world_base.dt)
        
        # Optimal intervention
        forcings_opt = adapter_opt.forcings(step)
        world_opt.step(intervention_forcings=forcings_opt)
        m_opt = world_opt.diagnose_metrics(t=step * world_opt.dt)
        
        # Gel beads
        forcings_gel = gel_intervention.forcings(step)
        world_gel.step(intervention_forcings=forcings_gel)
        m_gel = world_gel.diagnose_metrics(t=step * world_gel.dt)
        
        if step % 40 == 0:
            print(f"Step {step:3d} (t={step*0.05:5.1f}s)")
            print(f"  Baseline | peak_vt={m_base['peak_vt']:6.2f} m/s | ω={m_base['core_omega']:.3f} 1/s")
            print(f"  Optimal  | peak_vt={m_opt['peak_vt']:6.2f} m/s | ω={m_opt['core_omega']:.3f} 1/s")
            print(f"  Gel Bead | peak_vt={m_gel['peak_vt']:6.2f} m/s | ω={m_gel['core_omega']:.3f} 1/s")
            print()
    
    # Final comparison
    omega_base_final = world_base.history["core_omega"][-1]
    omega_opt_final = world_opt.history["core_omega"][-1]
    omega_gel_final = world_gel.history["core_omega"][-1]
    
    print("=" * 70)
    print("FINAL RESULTS (at t=10s)")
    print("=" * 70)
    print(f"Baseline:            ω = {omega_base_final:.3f} 1/s")
    print(f"Optimal (4K/-500Pa): ω = {omega_opt_final:.3f} 1/s")
    print(f"Gel Beads:           ω = {omega_gel_final:.3f} 1/s")
    print()
    print(f"Optimal reduction:  {(1 - omega_opt_final/omega_base_final)*100:.1f}%")
    print(f"Gel bead reduction: {(1 - omega_gel_final/omega_base_final)*100:.1f}%")


if __name__ == "__main__":
    test_gel_beads()
