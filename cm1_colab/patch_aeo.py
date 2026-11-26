"""Add the AEOLUS cooling intervention to CM1's solve1.F (env-var controlled; inactive unless AEO_COOL_K > 0).

Rule (same as the 2D model): inside a ring that follows the vortex centre (minimum surface pressure),
the potential-temperature perturbation is clamped to at most  -AEO_COOL_K * shape, where
shape = exp(-((r-R)/W)^2) * exp(-((z-Z)/D)^2).  Energy removed = sum rho*cp*dtheta*Exner*dV.
"""
import sys
from pathlib import Path

src = Path(sys.argv[1])
s = src.read_text()
assert "AEOCOOL" not in s, "already patched"

decl = """
      ! ---- AEOLUS cooling intervention (env-var controlled) ----
      integer, save :: aeo_init = 0
      real, save :: aeo_k=0.0, aeo_r=500.0, aeo_w=250.0, aeo_z=600.0, aeo_d=125.0, aeo_t0=0.0, aeo_t1=0.0
      double precision, save :: aeo_j = 0.0d0, aeo_next = -1.0d0
      integer :: aeo_ic, aeo_jc, aeo_st, aeo_n
      real :: aeo_xc, aeo_yc, aeo_pmin, aeo_rr, aeo_shape, aeo_tgt, aeo_dth
      real :: aeo_vals(7)
      character(len=10), dimension(7) :: aeo_names = (/ 'AEO_COOL_K','AEO_R     ','AEO_W     ','AEO_Z     ', &
                                                       'AEO_D     ','AEO_T0    ','AEO_T1    ' /)
      character(len=64) :: aeo_s
"""

code = """
!--------------------------------------------------------------------
!  AEOLUS cooling intervention
      IF( aeo_init.eq.0 )THEN
        aeo_init = 1
        aeo_vals = (/ aeo_k, aeo_r, aeo_w, aeo_z, aeo_d, aeo_t0, aeo_t1 /)
        do aeo_n=1,7
          call get_environment_variable(trim(aeo_names(aeo_n)),aeo_s,status=aeo_st)
          if( aeo_st.eq.0 ) read(aeo_s,*) aeo_vals(aeo_n)
        enddo
        aeo_k = aeo_vals(1); aeo_r = aeo_vals(2); aeo_w = aeo_vals(3); aeo_z = aeo_vals(4)
        aeo_d = aeo_vals(5); aeo_t0 = aeo_vals(6); aeo_t1 = aeo_vals(7)
        print *,'AEOCOOL config K,R,W,Z,D,t0,t1 =',aeo_k,aeo_r,aeo_w,aeo_z,aeo_d,aeo_t0,aeo_t1
      ENDIF
      IF( aeo_k.gt.0.0 .and. mtime.ge.dble(aeo_t0) .and. mtime.lt.dble(aeo_t1) )THEN
        aeo_pmin = 1.0e30
        aeo_ic = 1
        aeo_jc = 1
        do j=1,nj
        do i=1,ni
          if( ppi(i,j,1).lt.aeo_pmin )then
            aeo_pmin = ppi(i,j,1)
            aeo_ic = i
            aeo_jc = j
          endif
        enddo
        enddo
        aeo_xc = xh(aeo_ic)
        aeo_yc = yh(aeo_jc)
        do k=1,nk
          if( zh(1,1,k).gt.(aeo_z+4.0*aeo_d) ) exit
          do j=1,nj
          do i=1,ni
            aeo_rr = sqrt( (xh(i)-aeo_xc)**2 + (yh(j)-aeo_yc)**2 )
            aeo_shape = exp(-((aeo_rr-aeo_r)/aeo_w)**2) * exp(-((zh(i,j,k)-aeo_z)/aeo_d)**2)
            if( aeo_shape.gt.1.0e-3 )then
              aeo_tgt = -aeo_k*aeo_shape
              aeo_dth = tha(i,j,k)-aeo_tgt
              if( aeo_dth.gt.0.0 )then
                tha(i,j,k) = aeo_tgt
                aeo_j = aeo_j + dble( rho0(i,j,k)*cp*aeo_dth*(pi0(i,j,k)+ppi(i,j,k))  &
                                     *(dx*ruh(i))*(dy*rvh(j))*(dz*rmh(i,j,k)) )
              endif
              th3d(i,j,k) = min( th3d(i,j,k), aeo_tgt )
            endif
          enddo
          enddo
        enddo
        if( mtime.ge.aeo_next )then
          print *,'AEOCOOL t,xc,yc,ppimin,J =',mtime,aeo_xc,aeo_yc,aeo_pmin,aeo_j
          aeo_next = mtime + 60.0d0
        endif
      ENDIF

"""

head = s.index("subroutine solve1(")
imp = s.index("implicit none\n", head) + len("implicit none\n")
s = s[:imp] + decl + s[imp:]
anchor = "!-----------------------------------------------------------------------------\n!  Convective parameterization:"
pos = s.index(anchor)
s = s[:pos] + code.lstrip("\n") + s[pos:]
src.write_text(s)
print("patched", src)
