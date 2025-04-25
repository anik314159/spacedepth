# On Exact Space-Depth Trade-Offs in Multi-Controlled Toffoli Decomposition
In this paper, we consider the optimized implementation of Multi Controlled Toffoli (MCT) using
the Clifford + T gate sets. While there are several recent works in this direction, here we explicitly
quantify the trade-off (with concrete formulae) between the Toffoli depth (this means the depth using
the classical 2-controlled Toffoli) of the n-controlled Toffoli (hereform we will tell n-MCT) and the
number of clean ancilla qubits. Additionally, we achieve a reduced Toffoli depth (and consequently,
T-depth), which is an extension of the technique introduced by Khattar et al. (2024). In terms
of a negative result, we first show that using such conditionally clean ancillae techniques, Toffoli
depth can never achieve exactly ⌈log2 n⌉, though it remains of the same order. This highlights the
limitation of the techniques exploiting conditionally clean ancillae [Nie et al., 2024, Khattar et al.,
2024]. Then we prove that, in a more general setup, the T-Depth in the Clifford + T decomposition,
via Toffoli gates, is lower bounded by ⌈log2 n⌉, and this bound is achieved following the complete
binary tree structure. Since the (2-controlled) Toffoli gate can further be decomposed using Clifford
+ T, various methodologies are explored too in this regard for trade-off related implications.
