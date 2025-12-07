"""
Myelinated Axon - Saltatory Conduction (v5)
===========================================

물리적 도약전도 (Saltatory Conduction) 모델

📐 수식:
    ∂V/∂t = D(x)∂²V/∂x² - g_L(x)(V - E_L)/C_m(x)
             + [I_ext(x,t) + I_Na_node(x,t)]/C_m(x)
             - γ_extra(V - V_rest)

    Node only:
        I_Na_node = g_Na_node·m³·h·(E_Na_node - V)
        ḿ = (m_inf(V) - m)/τ_m
        ḣ = (h_inf(V) - h)/τ_h

특징:
    - 노드(Node)와 인터노드(Internode) 구간 구분
    - 각 구간의 확산(D), 막용량(Cm), 누설전도(gL) 상이
    - 노드에서만 빠른 Na⁺ 채널 활성화
    - CFL 안정조건 기반 자동 서브스텝 분할
    - 도약전도 속도 측정

Author: GNJz (Qquarts)
Version: 5.0.0 (Saltatory Conduction Edition)
"""

import numpy as np
from typing import Dict, Any, Optional


# 도약전도 기본 설정
MYELINATED_AXON_CONFIG = {
    "N": 121,  # 총 그리드 포인트 수
    "node_period": 10,  # 노드 간격 (10개 포인트마다 노드)
    "Vrest": -70.0,  # 안정 전위 (mV)
    "tau": 1.0,  # 시간 상수 (ms)
    "dx": 1e-3,  # 공간 간격 (cm)
    "cfl_safety": 0.5,  # CFL 안정성 계수
    
    # 구간별 물리 파라미터
    "D_node": 0.5,  # 노드 확산 계수 (cm²/ms)
    "D_internode": 0.01,  # 인터노드 확산 계수 (cm²/ms)
    "Cm_node": 1.0,  # 노드 막용량 (μF/cm²)
    "Cm_myelin": 0.01,  # 수초 막용량 (μF/cm²)
    "gL_node": 0.1,  # 노드 누설 전도도 (mS/cm²)
    "gL_myelin": 0.001,  # 수초 누설 전도도 (mS/cm²)
    "EL": -70.0,  # 누설 전위 (mV)
    
    # 전류 결합 / 자극
    "thresh": -20.0,  # 임계값 (mV)
    "coupling": 0.1,  # 소마 결합 계수
    "stim_gain": 1.0,  # 자극 이득
    
    # 노드 Na 채널 파라미터
    "node_ENa": 50.0,  # Na 역전위 (mV)
    "node_m_tau": 0.1,  # m 게이트 시간 상수 (ms)
    "node_h_tau": 0.5,  # h 게이트 시간 상수 (ms)
    "node_m_inf_k": 5.0,  # m_inf 시그모이드 기울기
    "node_m_inf_Vh": -40.0,  # m_inf 시그모이드 중심
    "node_h_inf_k": -5.0,  # h_inf 시그모이드 기울기
    "node_h_inf_Vh": -50.0,  # h_inf 시그모이드 중심
    
    # Inflation / 감쇠 계수
    "c0": 1.0,  # 초기 inflation 계수
    "Lambda": 0.0,  # 시간 감쇠 계수 (per ms)
    "gamma_decay": 0.0,  # 추가 감쇠 계수
    
    # α-pulse 파라미터 (선택적)
    "alpha_I0": 0.0,  # α-펄스 진폭
    "alpha_tau_r": 0.5,  # α-펄스 상승 시간 (ms)
    "alpha_tau_d": 3.0,  # α-펄스 감쇠 시간 (ms)
}


class MyelinatedAxon:
    """
    도약전도 (Saltatory Conduction) 모델
    
    소마에서 전송된 활동전위가 축삭을 따라 도약전도로 전달되는 과정 모델링
    - 노드(Node)와 인터노드(Internode) 구간 구분
    - 각 구간의 확산(D), 막용량(Cm), 누설전도(gL) 상이
    - 노드에서만 빠른 Na⁺ 채널 활성화
    - CFL 안정조건 기반 자동 서브스텝 분할
    
    Attributes:
        V: 막전위 배열 (N개 포인트)
        m_node, h_node: 노드 Na 채널 게이트 변수
        first_cross_ms: 노드 통과 시간 기록 (속도 측정용)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        도약전도 축삭 초기화
        
        Parameters
        ----------
        config : dict, optional
            축삭 설정 (기본값: MYELINATED_AXON_CONFIG)
        """
        # 설정 병합
        if config is None:
            config = MYELINATED_AXON_CONFIG.copy()
        else:
            cfg = MYELINATED_AXON_CONFIG.copy()
            cfg.update(config)
            config = cfg
        
        # 그리드 설정
        self.N = int(config["N"])
        self.NODE_STEP = int(config["node_period"])
        self.NODE_IDX = list(range(0, self.N, self.NODE_STEP))
        self.IS_NODE = np.zeros(self.N, dtype=bool)
        self.IS_NODE[self.NODE_IDX] = True
        
        # 기본 상수
        self.Vrest = float(config["Vrest"])
        self.tau = float(config["tau"])
        self.dx = float(config["dx"])
        self.cfl_safety = float(config["cfl_safety"])
        
        # 구간별 물리 파라미터
        self.D_node = float(config["D_node"])
        self.D_internode = float(config["D_internode"])
        self.Cm_node = float(config["Cm_node"])
        self.Cm_myelin = float(config["Cm_myelin"])
        self.gL_node = float(config["gL_node"])
        self.gL_myelin = float(config["gL_myelin"])
        self.EL = float(config["EL"])
        
        # 전류 결합 / 자극
        self.thresh = float(config["thresh"])
        self.coupling = float(config["coupling"])
        self.stim_gain = float(config["stim_gain"])
        
        # 전위 초기화
        self.V = np.full(self.N, self.Vrest, dtype=float)
        
        # 노드 전용 Na 게이트
        self.node_gNa = 800.0  # 노드 Na 전도도 (mS/cm²)
        self.node_ENa = float(config["node_ENa"])
        self.m_tau = float(config["node_m_tau"])
        self.h_tau = float(config["node_h_tau"])
        self.m_inf_k = float(config["node_m_inf_k"])
        self.m_inf_Vh = float(config["node_m_inf_Vh"])
        self.h_inf_k = float(config["node_h_inf_k"])
        self.h_inf_Vh = float(config["node_h_inf_Vh"])
        
        self.m_node = np.zeros(self.N)
        self.h_node = np.zeros(self.N)
        self.m_node[self.IS_NODE] = 0.05
        self.h_node[self.IS_NODE] = 0.60
        
        # 속도 측정용
        self.first_cross_ms = {i: None for i in self.NODE_IDX}
        
        # Inflation / 감쇠 계수
        self.c0 = float(config.get("c0", 1.0))
        self.Lambda = float(config.get("Lambda", 0.0))
        self.gamma_extra = float(config.get("gamma_decay", 0.0))
        
        # α-pulse 파라미터
        self.alpha_I0 = float(config.get("alpha_I0", 0.0))
        self.alpha_tr = float(config.get("alpha_tau_r", 0.5))
        self.alpha_td = float(config.get("alpha_tau_d", 3.0))
        self.alpha_ts = []  # spike timestamps (ms)
        
        # ATP 수준 (선택적)
        self.ATP_level = None
    
    @staticmethod
    def _sigmoid(x):
        """시그모이드 함수"""
        x = np.clip(x, -120.0, 120.0)
        return 1.0 / (1.0 + np.exp(-x))
    
    def _node_m_inf(self, V):
        """m_inf(V) = σ((V - Vh_m)/k_m)"""
        return self._sigmoid((V - self.m_inf_Vh) / self.m_inf_k)
    
    def _node_h_inf(self, V):
        """h_inf(V) = σ((V - Vh_h)/k_h)"""
        return self._sigmoid((V - self.h_inf_Vh) / self.h_inf_k)
    
    def _laplacian(self, V):
        """공간 2차 미분 (Laplace Operator)"""
        lap = np.zeros_like(V)
        dx2 = self.dx ** 2
        lap[1:-1] = (V[:-2] - 2 * V[1:-1] + V[2:]) / dx2
        # Neumann 경계조건: ∂V/∂x = 0
        lap[0] = 2.0 * (V[1] - V[0]) / dx2
        lap[-1] = 2.0 * (V[-2] - V[-1]) / dx2
        return lap
    
    def _calc_dt_cfl(self):
        """CFL 안정조건 (dt ≤ dx² / (2D))"""
        Dmax = max(self.D_node, self.D_internode)
        return self.cfl_safety * (self.dx ** 2) / (2.0 * Dmax)
    
    def _update_node_gates(self, dt):
        """노드 게이트 업데이트"""
        Vi = self.V[self.IS_NODE]
        m_inf = self._node_m_inf(Vi)
        h_inf = self._node_h_inf(Vi)
        self.m_node[self.IS_NODE] += dt * (m_inf - self.m_node[self.IS_NODE]) / self.m_tau
        self.h_node[self.IS_NODE] += dt * (h_inf - self.h_node[self.IS_NODE]) / self.h_tau
        self.m_node = np.clip(self.m_node, 0.0, 1.0)
        self.h_node = np.clip(self.h_node, 0.0, 1.0)
    
    def _node_Na_current(self):
        """노드 Na 전류 (ATP 의존 전도도 조정 포함)"""
        INa = np.zeros(self.N)
        idx = np.where(self.IS_NODE)[0]
        if idx.size:
            m3h = (self.m_node[idx] ** 3) * self.h_node[idx]
            
            # ATP 의존 Na 전도도 조정
            if self.ATP_level is not None:
                A0 = 100.0
                dA = 50.0
                lambda_A = 0.25
                gNa_eff = self.node_gNa * (1.0 + lambda_A * np.tanh((self.ATP_level - A0) / dA))
            else:
                gNa_eff = self.node_gNa
            
            INa[idx] = gNa_eff * m3h * (self.node_ENa - self.V[idx])
        return INa
    
    def trigger_alpha(self, t_ms: float):
        """소마 스파이크 발생 시 호출 (α-펄스 트리거)"""
        self.alpha_ts.append(float(t_ms))
    
    def _alpha_kernel(self, t_ms: float):
        """α-펄스 커널: I_α(t) = I₀[exp(−(t−t₀)/τ_d) − exp(−(t−t₀)/τ_r)]₊"""
        if self.alpha_I0 == 0.0 or not self.alpha_ts:
            return 0.0
        val = 0.0
        for t0 in self.alpha_ts:
            dt = t_ms - t0
            if dt <= 0.0:
                continue
            val += (np.exp(-dt / self.alpha_td) - np.exp(-dt / self.alpha_tr))
        return max(0.0, val) * self.alpha_I0
    
    def _record_crossings(self, t_ms):
        """노드 전위 임계 통과 기록 (속도 측정용)"""
        for i in self.NODE_IDX:
            if self.first_cross_ms[i] is None and self.V[i] >= self.thresh:
                self.first_cross_ms[i] = t_ms
    
    def step(self, dt_elec: float, t_ms: float, I0_from_soma: float, soma_V: float):
        """
        한 시점에서의 축삭 전도 계산
        
        Parameters
        ----------
        dt_elec : float
            전기적 시간 간격 (ms)
        t_ms : float
            현재 시간 (ms)
        I0_from_soma : float
            소마로부터의 전류 (μA)
        soma_V : float
            소마 막전위 (mV)
        """
        # CFL 기반 서브스텝 분할
        dt_cfl = self._calc_dt_cfl()
        n_sub = max(1, int(np.ceil(dt_elec / max(1e-12, dt_cfl))))
        dt_sub = dt_elec / n_sub
        
        for _ in range(n_sub):
            self._update_node_gates(dt_sub)
            
            # 구간별 파라미터 분포
            D = np.full(self.N, self.D_internode)
            D[self.IS_NODE] = self.D_node
            Cm = np.full(self.N, self.Cm_myelin)
            Cm[self.IS_NODE] = self.Cm_node
            gL = np.full(self.N, self.gL_myelin)
            gL[self.IS_NODE] = self.gL_node
            
            # 외부 자극 (소마 결합)
            I_ext = np.zeros(self.N)
            I_ext[0] = I0_from_soma + self.coupling * (soma_V - self.V[0])
            
            # 노드 Na 전류
            I_Na = self._node_Na_current()
            
            # 확산항 계산
            lap = self._laplacian(self.V)
            
            # Inflation factor 적용
            c_t = self.c0 * np.exp(-self.Lambda * t_ms)
            D_eff = c_t * D
            
            # α-펄스 자극
            I_alpha0 = self._alpha_kernel(t_ms)
            if I_alpha0 != 0.0:
                I_ext[0] += I_alpha0
            
            # 추가 감쇠항
            extra_decay = -self.gamma_extra * (self.V - self.Vrest)
            
            # 막전위 변화율
            dVdt = D_eff * lap - gL * (self.V - self.EL) / Cm + (I_ext + I_Na) / Cm + extra_decay
            
            # 막전위 갱신
            self.V += dt_sub * dVdt
            
            # 전체 막전위 clamp [-90, 50] mV
            self.V = np.clip(self.V, -90.0, 50.0)
            
            # 노드 통과 시간 기록
            self._record_crossings(t_ms)
    
    def velocity_last(self) -> float:
        """
        노드 통과 시간 차이 기반 평균 전도속도 계산
        
        Returns
        -------
        float
            전도속도 (m/s)
        """
        times = [self.first_cross_ms[i] for i in self.NODE_IDX if self.first_cross_ms[i] is not None]
        if len(times) < 2:
            return 0.0
        arr = np.array(times)
        dt = np.diff(arr)
        dt = dt[dt > 0.0]
        if dt.size == 0:
            return 0.0
        mean_dt_ms = float(np.mean(dt))
        dist_cm = self.NODE_STEP * self.dx
        v_m_s = (dist_cm / (mean_dt_ms * 1e-3)) * 0.01  # cm/ms → m/s
        return v_m_s
    
    def reset(self):
        """초기 상태로 리셋"""
        self.V = np.full(self.N, self.Vrest, dtype=float)
        self.m_node = np.zeros(self.N)
        self.h_node = np.zeros(self.N)
        self.m_node[self.IS_NODE] = 0.05
        self.h_node[self.IS_NODE] = 0.60
        self.first_cross_ms = {i: None for i in self.NODE_IDX}
        self.alpha_ts = []
    
    def get_state(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            "V": self.V.copy(),
            "m_node": self.m_node.copy(),
            "h_node": self.h_node.copy(),
            "velocity": self.velocity_last(),
        }

