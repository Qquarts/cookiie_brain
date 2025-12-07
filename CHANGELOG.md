# Changelog

All notable changes to BabyHippo will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.3.0] - 2025-12-07 (Cookie v1.0 - 1st Cookie Revolution)

### 🍪 Added - Cookie v1.0 Features
- **Concept Neuron Selectivity**: Enhanced pattern separation for individual neurons
- **Sleep/Consolidation/Recall Tuning**: Improved memory consolidation accuracy (70% → 90%)
- **Conversation Context Management**: Added context tracking for natural dialogue
- **Question/Learning Command Detection**: Accurate distinction between questions and learning commands
- **Library Integration**: Automatic learning from external LLM API responses
- **Personal Library Growth**: Knowledge accumulation from library visits

### 🔧 Improved
- **Question Detection**: Enhanced pattern recognition for questions
- **Memory Recall**: Better accuracy in retrieving learned information
- **Context Understanding**: Improved dialogue flow and continuity
- **Error Correction**: Added "아니야" (no/correction) handling

### 🐛 Fixed
- Fixed question/learning command confusion
- Fixed memory recall returning questions as answers
- Fixed conversation context not being utilized
- Fixed library learning algorithm not triggering

## [4.2.0] - 2025-XX-XX (Body & Soul Edition)

### 🆕 Added
- **Body System**: Complete peripheral nervous system implementation
  - `body/senses.py`: Sensory input (Eyes, Ears, Text)
  - `body/actions.py`: Motor output (Speech, Text, Motor)
  - `body/nervous_system.py`: Central coordinator connecting brain and body
- **Dream Manager**: Sleep orchestration and memory consolidation
- **Neuron Models**: Multiple neuron model options
  - `HHSomaQuick`: Optimized Hodgkin-Huxley (Flyweight Pattern)
  - `IzhikevichNeuron`: Efficient neuron model (v3)
  - `HHLIFNeuron`: Hybrid HH-LIF model (v4)
  - `MyelinatedAxon`: Saltatory conduction model (v5)
- **PanoramaMemory**: Multi-tier memory system (Archive, Timeline, Surface)
- **CuriousBrain**: Integration of memory, LLM, and external library

### 🔧 Improved
- Memory system with better consolidation
- Sleep/wake cycle implementation
- STDP synapse learning

### 🐛 Fixed
- Memory footprint optimization (Flyweight Pattern for HHSomaQuick)
- Initialization time reduction

## [4.1.0] - 2025-XX-XX

### 🆕 Added
- Hippocampal memory system
- STDP learning mechanism
- Sleep consolidation

## [4.0.0] - 2025-XX-XX

### 🆕 Initial Release
- 8 core brain modules
- DNA personality system
- Basic memory system

---

## Version History

- **4.3.0**: Cookie v1.0 - 1st Cookie Revolution (Current)
- **4.2.0**: Body & Soul Edition
- **4.1.0**: Hippocampal Memory System
- **4.0.0**: Initial Release

---

## Future Roadmap

See [docs/ARCHITECTURE_ROADMAP.md](docs/ARCHITECTURE_ROADMAP.md) for detailed future plans.

### Phase 1: Synapse Engine Enhancement
- Propagation delay
- Synapse fatigue
- AMPA/NMDA ratio
- STDP accuracy improvements

### Phase 2: Hippocampal Network Topology
- DG→CA3 branching
- CA3 recurrent network
- CA1 synaptic alignment

### Phase 3: Energy Metabolism Integration
- ATP ↔ axonal conduction feedback

### Phase 4: Large-Scale Optimization
- Vectorization (NumPy)
- Parallelization
- Distributed computing

