Exact dipolar moments of a localized electric current distribution

Ivan Fernandez-Corbaton*

Institute of Nanotechnology, Karlsruhe Institute of Technology, 76021 Karlsruhe, Germany

Stefan Nanz and Rasoul Alaee'institut für Theoretische Festkörperphysik, Karlsruhe Institute of Technology, 76131 Karlsruhe, Germany

Carsten RockstuhlInstitut für Theoretische Festkörperphysik, Karlsruhe Institute of Technology, 76131 Karlsruhe, Germany andInstitute of Nanotechnology, Karlsruhe Institute of Technology, 76021 Karlsruhe, Germany

The multipolar decomposition of current distributions is used in many branches of physics. Here, we obtain new exact expressions for the dipolar moments of a localized electric current distribution. The typical integrals for the dipole moments of electromagnetically small sources are recovered as the lowest order terms of the new expressions in a series expansion with respect to the size of the source. All the higher order terms can be easily obtained. We also provide exact and approximated expressions for dipoles that radiate a definite polarization handedness (helicity). Formally, the new exact expressions are only marginally more complex than their lowest order approximations.

The multipolar decomposition of a spatially confined electromagnetic source distribution is a basic tool in both classical and quantum electrodynamics [1-5]. On the one hand, the multipolar coefficients determine the coupling of the source to external electromagnetic fields. This is used in the study of molecular, atomic, and nuclear electromagnetic interactions. On the other hand, there is a one-to-one correspondence between the multipolar components of the source and the multipolar fields radiated by it. This is exploited in the understanding and design of radiating systems. For example, in nanophotonics, the multipole moments of induced current distributions are used to study optical nano-antennas and meta-atoms [6-9]. The multipolar decomposition can be done in different ways, e.g. [2, Chap. 9] and [10, App. B, §4], resulting in integral expressions for the multipolar coefficients. The exact expressions are considerably simplified in the limit of electromagnetically small sources, but artificial scatterers at optical frequencies are typically large enough to compromise the accuracy of the approximation.

# I. OUTLINE

In this article, we obtain new exact expressions for the source dipolar moments [Eqs. (20)-(22)]. In particular, they are valid for any source size. We start our derivation in momentum space exploiting the fact that the fields radiated by the source at a given frequency $\omega$ are determined solely by its momentum components in a spherical shell of radius $\omega/c$, where $c$ is the speed of light in the medium. We first obtain hybrid integrals in momentum and coordinate space for all multipolar orders. In the dipolar case, we bring them to a form that is only marginally more complex than the typical integrals that

give the dipolar moments of electromagnetically small sources. The additional complexity is the appearance of spherical Bessel functions. We identify the spherical Bessel functions as the elements that perform the necessary selection of the appropriate momentum shell. When the spherical Bessel functions are expanded around zero, the typical approximations for the magnetic and electric moments of electromagnetically small sources are recovered as the lowest order terms in the expansion. The toroidal dipole is recovered as the second term in the electric case. All higher order corrections are easily obtained as successive terms of the expansions. We include integral expressions for the magnetic corrections of order $k^{3}$ and the electric/toroidal corrections of order $k^{4}$. We also provide exact and approximated expressions for dipoles that radiate a definite polarization handedness (helicity) [Eq. (40) and Eq. (41)].

# II. PROBLEM SETTING

We start by considering an electric current density distribution $\mathbf{J}(\mathbf{r},t)$ embedded in an infinite, isotropic, and homogeneous medium characterized by real valued permittivity $\epsilon$ and permeability $\mu$. We assume $\mathbf{J}(\mathbf{r},t)$ to be confined in space so that $\mathbf{J}(\mathbf{r},t)=0$ for $|\mathbf{r}|>R$. We consider its energy-momentum Fourier representation

$$
\begin{array}{rl} & { \mathbf { J } ( \mathbf { r } , t ) = \mathcal { R } \left[ \int _ { 0 ^{+} } ^{\infty} \frac { d \omega } { \sqrt { 2 \pi } } \exp \left( - i \omega t \right) \mathbf { J } _ { \omega } ( \mathbf { r } ) \right] } \\& { = \mathcal { R } \left[ \int _ { 0 ^{+} } ^{\infty} \frac { d \omega } { \sqrt { 2 \pi } } \exp \left( - i \omega t \right) \int \frac { d ^{3} \mathbf { p } } { \sqrt { ( 2 \pi ) ^{3} } } \, \mathbf { J } _ { \omega } ( \mathbf { p } ) \exp \left( i \mathbf { p } \cdot \mathbf { r } \right) \right] , } \end{array}
$$

and treat each $\omega$ term separately. The frequency $\omega$ and the three components of the momentum vector $\mathbf{p}$ are real numbers. The lower limit of the integral in $d\omega$ excludes

the static case $\omega=0$, which we do not treat in this paper. At each frequency $\omega$, the transverse electromagnetic fields outside the source are solely determined by the part of $\mathbf{J}_{\omega}(\mathbf{p})$ in the domain that satisfies $|\mathbf{p}|=\omega/c$. This result was obtained by Devaney and Wolf [11]. We provide an alternative proof in App. A.

We denote by $\tilde{\mathbf{J}}_{\omega}(\hat{\mathbf{p}})$ the components of $\mathbf{J}_{\omega}(\mathbf{p})$ in the spherical shell of radius $|\mathbf{p}|=\omega/c$. The symbol $\hat{\mathbf{p}}$ represents the angular part of the momentum vector $\mathbf{p}$, i.e., the solid angle in the spherical shell. As usual, we define $k=\omega/c$.

We will expand $\tilde{\mathbf{J}}_{\omega}(\tilde{\mathbf{p}})$ in an orthonormal basis for functions defined in a spherical shell: The three families of multipolar functions in momentum space [3, B$_{I}$,3]

$$
\begin{array}{r} { \mathbf { X } _ { j m } ( \hat { \mathbf { p } } ) = \frac { 1 } { \sqrt { j ( j + 1 ) } } \mathbf { L } Y _ { j m } ( \hat { \mathbf { p } } ) , } \\{ \mathbf { Z } _ { j m } ( \hat { \mathbf { p } } ) = i \hat { \mathbf { p } } \times \mathbf { X } _ { j m } ( \hat { \mathbf { p } } ) , } \\{ \mathbf { W } _ { j m } ( \hat { \mathbf { p } } ) = \hat { \mathbf { p } } Y _ { j m } ( \hat { \mathbf { p } } ) . } \end{array}
$$

The $Y_{jm}(\hat{\mathbf{p}})$ are the spherical harmonics and the three components of the vector $\mathbf{L}$ are the angular momentum operators for scalar functions.

Each of the vector multipolar functions in the three families is an eigenstate of the total angular momentum squared $J^2$ and the angular momentum along one axis $\hat{\mathbf{q}}$, for which we choose $\hat{\mathbf{q}}=\hat{\mathbf{z}}$. With $\mathbf{Q}_{jm}(\hat{\mathbf{p}})$ standing for any of the $\{\mathbf{X}_{jm}(\hat{\mathbf{p}}),\mathbf{Z}_{jm}(\hat{\mathbf{p}}),\mathbf{W}_{jm}(\hat{\mathbf{p}})\}$:

$$
J ^{2} \mathbf { Q } _ { j m } ( \hat { \mathbf { p } } ) = j ( j + 1 ) \mathbf { Q } _ { j m } ( \hat { \mathbf { p } } ) , \ J _ { z } \mathbf { Q } _ { j m } ( \hat { \mathbf { p } } ) = m \mathbf { Q } _ { j m } ( \hat { \mathbf { p } } ) .
$$

where $j$ and $m$ are integers, and $m = -j \ldots j$. For $\mathbf{X}_{jm}(\hat{\mathbf{p}})$ and $\mathbf{Z}_{jm}(\hat{\mathbf{p}})$, $j$ takes integer values in $j > 0$, while for $\mathbf{W}_{jm}(\hat{\mathbf{p}})$, $j = 0$ is also possible.

The functions in Eq. (2) are also eigenstates of the parity operator$^{1}$:

$$
\begin{array}{rl} & { \Pi \mathbf { X } _ { j m } ( \hat { \mathbf { p } } ) = - \mathbf { X } _ { j m } ( - \hat { \mathbf { p } } ) = ( - 1 ) ^{j + 1} \mathbf { X } _ { j m } ( \hat { \mathbf { p } } ) , } \\& { \Pi \mathbf { Z } _ { j m } ( \hat { \mathbf { p } } ) = - \mathbf { Z } _ { j m } ( - \hat { \mathbf { p } } ) = ( - 1 ) ^{j} \mathbf { Z } _ { j m } ( \hat { \mathbf { p } } ) , } \\& { \Pi \mathbf { W } _ { j m } ( \hat { \mathbf { p } } ) = - \mathbf { W } _ { j m } ( - \hat { \mathbf { p } } ) = ( - 1 ) ^{j} \mathbf { W } _ { j m } ( \hat { \mathbf { p } } ) . } \end{array}
$$

The polarization of $\mathbf{X}_{jm}(\hat{\mathbf{p}})$ and $\mathbf{Z}_{jm}(\hat{\mathbf{p}})$ is transverse (orthogonal) to $\hat{\mathbf{p}}$, and the polarization of $\mathbf{W}_{jm}(\hat{\mathbf{p}})$ is longitudinal (parallel) to $\hat{\mathbf{p}}$, as depicted in Fig. 1. In coordinate ($\mathbf{r}$) space, this distinction corresponds to the distinction between divergence free (transverse) and curl free (longitudinal) fields.

With the scalar product

$$
\langle A | B \rangle = \int d \hat { \mathbf { p } } \, \mathbf { A } ^{\dagger} ( \hat { \mathbf { p } } ) \mathbf { B } ( \hat { \mathbf { p } } ) ,
$$

where $^\dagger$ denotes hermitian transpose, and $\hat{\mathbf{p}}$ runs over the entire spherical shell, the three families together form an orthonormal basis for functions defined on any spherical shell in momentum space.

We expand $\mathbf{J}_{\omega}(\hat{\mathbf{p}})$ in this basis:

$$
\mathbf { \hat { J } } _ { \omega } ( \hat { \mathbf { p } } ) = \sum _ { j m } a _ { j m } ^{\omega} \mathbf { Z } _ { j m } ( \hat { \mathbf { p } } ) + b _ { j m } ^{\omega} \mathbf { X } _ { j m } ( \hat { \mathbf { p } } ) + c _ { j m } ^{\omega} \mathbf { W } _ { j m } ( \hat { \mathbf { p } } ) ,
$$

where, with $q_{jm}^{\omega}$ standing for any of the $\{a_{jm}^{\omega}, b_{jm}^{\omega}, c_{jm}^{\omega}\}$,

$$
\hat { q } _ { j m } ^{\omega} = \langle Q _ { j m } | \hat { \mathbf { J } } _ { \omega } \rangle = \int d \hat { \mathbf { p } } \mathbf { Q } _ { j m } ^{\dagger} ( \hat { \mathbf { p } } ) \hat { \mathbf { J } } _ { \omega } ( \hat { \mathbf { p } } ) .
$$

![](images/79a532fe10e278881878bbe305c3bf4076ff158c8562e8f365d48a2f5647dccd_26.jpg){width=26%} FIG. 1. The electromagnetic field radiated by a confined monochromatic current density $\mathbf{J}_{\omega}(\mathbf{r})$ with Fourier transform $\mathbf{J}_{\omega}(\mathbf{p})$ only depends on the components of $\mathbf{J}_{\omega}(\mathbf{p})$ in a spherical shell of radius $|\mathbf{p}|=\omega/c$. The relevant part of $\mathbf{J}_{\omega}(\mathbf{p})$ can hence be expressed as a linear combination of the momentum space vector multipolar functions $\{\mathbf{X}_{jm}(\hat{\mathbf{p}}),\mathbf{Z}_{jm}(\hat{\mathbf{p}}),\mathbf{W}_{jm}(\hat{\mathbf{p}})\}$, which form an orthonormal basis for functions defined on the shell. The polarization vectors of $\mathbf{X}_{jm}(\hat{\mathbf{p}})$ and $\mathbf{Z}_{jm}(\hat{\mathbf{p}})$ are tangential to the surface of the shell, i.e., orthogonal (transverse) to the momentum vector $\mathbf{p}$. The polarization vector of $\mathbf{W}_{jm}(\hat{\mathbf{p}})$ is normal to the surface of the shell, i.e., parallel (longitudinal) to $\mathbf{p}$.

The {$a_{jm}^{\omega}$, $b_{jm}^{\omega}$, $c_{jm}^{\omega}$} coefficients contain all the information about $\mathbf{J}_{\omega}(\hat{\mathbf{p}})$ so they must also contain all the information about the fields produced by it. As shown in [11], the {$a_{jm}^{\omega}$, $b_{jm}^{\omega}$} determine the transverse electromagnetic field radiated by the sources at frequency $\omega$ outside a spherical volume enclosing them: They are the coefficients of the expansion of the transverse fields in outgoing electric and magnetic multipoles, respectively [2, Eq. 9.122]. Therefore, the transverse components of $\hat{\mathbf{J}}_{\omega}(\hat{\mathbf{p}})$

determine the transverse components of the electromagnetic field at frequency $\omega$ outside the source region. The longitudinal electric field with $|\mathbf{p}|=\omega/c$ is zero outside the source region. While the longitudinal degrees of freedom of $\mathbf{J}_{\omega}(\hat{\mathbf{p}})$, i.e. the $c_{jm}^{\omega}$, are not necessarily equal to zero, the field that they generate outside the source region is canceled by the field generated by the charge density. This can be seen in [12, §13.3 p1875-1877], and in [13, App. C] where the cancellation is shown to be a consequence of the continuity equation. We will keep the $c_{jm}^{\omega}$ in the discussion both for completeness and because they play an important role in understanding the split of the $a_{jm}^{\omega}$ into electrical and toroidal parts [14–16], which we discuss in [13].

The {$a_{jm}^{\omega}, b_{jm}^{\omega}$} coefficients are a valuable source of information in many branches of physics. In molecular, atomic and nuclear physics, the {$a_{jm}^{\omega}, b_{jm}^{\omega}$} coefficients are used to describe the interaction of systems of charges with external electromagnetic fields, e.g. [4, Chap. 10], [3, IV.C.2c]) and [5, Chap. 7]. In classical electrodynamics they are used to describe radiation by source distributions, e.g. [1, Chap. 9] and [2, Chap. 9]. In nanophotonics, they are used to study and design the response of individual artificial nanostructures.

Given $\mathbf{J}_{\omega}(\mathbf{r})$, there exist exact expressions for the $\{a_{jm}^{\omega},b_{jm}^{\omega}\}$ as coordinate space integrals, e.g. [5, Eq. (7.20)]

$$
\begin{array}{r} { \tilde { a } _ { j m } ^{\omega} = \frac { 1 } { k } \int d ^{3} \mathbf { r } \ \left( \nabla \times j _ { j } ( k r ) \mathbf { X } _ { j m } ( \hat { \mathbf { r } } ) \right) ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) , } \\{ \tilde { b } _ { j m } ^{\omega} = \int d ^{3} \mathbf { r } \ j _ { j } ( k r ) \mathbf { X } _ { j m } ^{\dagger} ( \hat { \mathbf { r } } ) \mathbf { J } _ { \omega } ( \mathbf { r } ) , } \end{array}
$$

or, [2, Eq. (9.165) without the magnetization current therein],

$$
\begin{array}{r} { \hat { a } _ { j m } ^{\omega} = \frac { i k } { \sqrt { j ( j + 1 ) } } \int d ^{3} \mathbf { r } \; \, j _ { j } ( k r ) Y _ { j m } ^{*} ( \hat { \mathbf { r } } ) \mathbf { L } \cdot ( \nabla \times \mathbf { J } _ { \omega } ( \mathbf { r } ) ) , } \\{ \hat { b } _ { j m } ^{\omega} = \frac { - k ^{2} } { \sqrt { j ( j + 1 ) } } \int d ^{3} \mathbf { r } \; \, j _ { j } ( k r ) Y _ { j m } ^{*} ( \hat { \mathbf { r } } ) \mathbf { L } \cdot \mathbf { J } _ { \omega } ( \mathbf { r } ) , } \end{array}
$$

where the tildes and carets in the left hand sides indicate different normalizations, $r = |\mathbf{r}|$, $\hat{\mathbf{r}} = \mathbf{r}/|\mathbf{r}|$ is the angular part of $\mathbf{r}$, and $k \equiv \omega/c$ throughout the article.

The expressions in Eq. (8) and Eq. (9) are valid for any source radius $R$. For electromagnetically small sources where $kR \ll 1$, they can be reduced to the simpler well known expressions that are obtained in [2, Chap. 9] and [1, Chap. 9] by starting with the equation for the vector potential as a function of $\mathbf{J}_{\omega}(\mathbf{r})$ in the Lorentz gauge [Eq. (A2)], and expanding $\frac{\exp(i k|\mathbf{r}-\mathbf{r}^{\prime}|)}{|\mathbf{r}-\mathbf{r}^{\prime}|}$ in powers of $k|\mathbf{r}-\mathbf{r}^{\prime}|$. For example, when $kR \ll 1$ the source dependent terms of the electric and magnetic dipole moments are

$$
\begin{array}{r} { \left[ \begin{array}{l} { a _ { 11 } ^{\omega} } \\{ a _ { 10 } ^{\omega} } \end{array} \right] \rightarrow \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) , \ \left[ \begin{array}{l} { b _ { 11 } ^{\omega} } \\{ b _ { 10 } ^{\omega} } \end{array} \right] \rightarrow \int d ^{3} \mathbf { r } \ \mathbf { r } \times \mathbf { J } _ { \omega } ( \mathbf { r } ) , } \end{array}
$$

where we have chosen the spherical vector basis. We will work in this basis throughout the article. Appendix C contains auxiliary expressions.

# III. EXACT DIPOLAR MOMENTS

We will now obtain exact expressions for the dipolar vectors $[a_{11}^{\omega},a_{10}^{\omega},a_{1-1}^{\omega}]^{T}$, $[b_{11}^{\omega},b_{10}^{\omega},b_{1-1}^{\omega}]^{T}$ and $[c_{11}^{\omega},c_{10}^{\omega},c_{1-1}^{\omega}]^{T}$ as coordinate space integrals of functions of $\mathbf{J}_{\omega}(\mathbf{r})$. While these expressions are, as Eq. (8) and Eq. (9), valid for any source size, they are only marginally more complex than their $kR\ll1$ limits: Namely, they contain spherical Bessel functions. As far as we know, these expressions have not been reported before.

We start from Eq. (7), where we substitute

$$
\mathbf { \hat { J } } _ { \omega } ( \hat { \mathbf { p } } ) = \frac { 1 } { \sqrt { ( 2 \pi ) ^{3} } } \int d ^{3} \mathbf { r } \, \mathbf { J } _ { \omega } ( \mathbf { r } ) \exp \left( - i \frac { \omega } { c } \hat { \mathbf { p } } \cdot \mathbf { r } \right) .
$$

to get

$$
\hat { q } _ { j m } ^{\omega} = \frac { 1 } { \sqrt { ( 2 \pi ) ^{3} } } \int d \hat { \mathbf { p } } \ \mathbf { Q } _ { j m } ^{\dagger} ( \hat { \mathbf { p } } ) \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) \exp \left( - i \frac { \omega } { c } \hat { \mathbf { p } } \cdot \mathbf { r } \right) .
$$

The condition $|\mathbf{p}|=\omega/c$ is enforced in the argument of the exponential. We now substitute the exponential for its expansion in spherical harmonics

$$
\exp \left( - i \frac { \omega } { c } \hat { \mathbf { p } } \cdot \mathbf { r } \right) = ( 4 \pi ) \sum _ { l , m } ( - i ) ^{\bar { l} } Y _ { \bar { l } m } ^{*} ( \hat { \mathbf { r } } ) Y _ { \bar { l } m } ( \hat { \mathbf { p } } ) j _ { \bar { l } } ( k | \mathbf { r } | ) ,
$$

where $j_{\bar{j}}(\cdot)$ is the $\bar{l}$-th order spherical Bessel function of the first kind. The result is:

$$
\begin{array}{rl} & { \frac { \sqrt { ( 2 \pi ) ^{3} } } { 4 \pi } q _ { j m } ^{\omega} = } \\& { \sum _ { \tilde { l } \tilde { m } } ( - i ) ^{\tilde { l} } \int d \hat { \mathbf { p } } \, \mathbf { Q } _ { j m } ^{\dagger} ( \hat { \mathbf { p } } ) Y _ { \tilde { l } \tilde { m } } ( \hat { \mathbf { p } } ) \int d ^{3} \mathbf { r } \, \mathbf { J } _ { \omega } ( \mathbf { r } ) Y _ { \tilde { l } \tilde { m } } ^{*} ( \hat { \mathbf { r } } ) j _ { \tilde { l } } ( k r ) . } \end{array}
$$

Equation (14) is an exact expression for the {$a_{jm}^{\omega}, b_{jm}^{\omega}, c_{jm}^{\omega}$} coefficients in terms of integrals in both momentum (shaded area) and coordinate space. As shown in App. B, only terms with $\bar{l}=j$ contribute to the $b_{jm}^{\omega}$, while the $a_{jm}^{\omega}$ and $c_{jm}^{\omega}$ get contributions from both $\bar{l}=j-1$ and $\bar{l}=j+1$. Additionally, it is possible to further simplify Eq. (14) in the dipolar ($j=1$) case without making any approximation. We now present the derivations for the magnetic dipole $b_{jm}^{\omega}$. Appendix D contains the derivations for $a_{1m}^{\omega}$ and $c_{1m}^{\omega}$. It also contains the $c_{00}$ case.

For the magnetic dipole, we particularize Eq. (14) for $\mathbf{Q}_{jm}(\hat{\mathbf{p}}) \rightarrow \mathbf{X}_{jm}(\hat{\mathbf{p}})$ and $j=1$, which implies $\bar{l}=1$:

$$
\begin{array}{rl} & { i \frac { \sqrt { ( 2 \pi ) ^{3} } } { 4 \pi } b _ { 1 m } ^{\omega} = } \\& { \sum _ { \overline { { m } } = - 1 } ^{\overline { { m} } = 1 } \int d \hat { \mathbf { p } } \ \mathbf { X } _ { 1 m } ^{\dagger} ( \hat { \mathbf { p } } ) Y _ { 1 \overline { { m } } } ( \hat { \mathbf { p } } ) \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) Y _ { 1 \overline { { m } } } ^{*} ( \hat { \mathbf { r } } ) j _ { 1 } ( k r ) . } \end{array}
$$

Explicit expressions of $\mathbf{X}_{1m}(\hat{\mathbf{p}})$ can be obtained using Eq. (C6) and then used to write the momentum integrals in the shaded area of Eq. (15) as

$$
\begin{aligned}&m=1\:\to\:\int d\mathbf{\hat{p}}\:\begin{bmatrix}-\frac{Y_{10}(\mathbf{\hat{p}})}{\sqrt{2}}\\\frac{Y_{11}(\mathbf{\hat{p}})}{\sqrt{2}}\\0\end{bmatrix}^{\dagger}Y_{1\overline{m}}(\mathbf{\hat{p}}),\\&m=0\:\to\:\int d\mathbf{\hat{p}}\:\begin{bmatrix}-\frac{Y_{1-1}(\mathbf{\hat{p}})}{\sqrt{2}}\\0\\\frac{Y_{11}(\mathbf{\hat{p}})}{\sqrt{2}}\end{bmatrix}^{\dagger}Y_{1\overline{m}}(\mathbf{\hat{p}}),\\&m=-1\:\to\:\int d\mathbf{\hat{p}}\:\begin{bmatrix}0\\-\frac{Y_{1-1}(\mathbf{\hat{p}})}{\sqrt{2}}\\\frac{Y_{10}(\mathbf{\hat{p}})}{\sqrt{2}}\end{bmatrix}^{\dagger}Y_{1\overline{m}}(\mathbf{\hat{p}})\end{aligned}
$$

which can be easily solved for each $\overline{m} \in \{-1,0,1\}$ using the orthonormality properties of the spherical harmonics: $\int d\hat{\mathbf{p}} \ Y_{lm}(\hat{\mathbf{p}}) Y_{lm}^{*}(\hat{\mathbf{p}}) = \delta_{\overline{m}m} \delta_{\hat{\mu}}$. They result in three vectors for each $m$ case, which we list here as row vectors. From top to bottom, the three row vectors correspond to $\overline{m} = 1, 0, -1$:

$$
\begin{aligned}m&=1\to\:\frac{1}{\sqrt{2}}\:(\:0\:1\:0\:),\\(\:-1\:0\:0\:),\\(\:0\:0\:0\:)\\m&=0\to\:\frac{1}{\sqrt{2}}\:(\:0\:0\:0\:),\\(\:-1\:0\:0\:)\\m&=-1\to\:\frac{1}{\sqrt{2}}\:(\:0\:0\:0\:).\end{aligned}
$$

Having solved the momentum space integrals in the shaded area of Eq. (15), the summation in $\overline{m}$ can now be done. With $\mathbf{J}_{\omega}(\mathbf{r})=[J_{1}^{\omega},J_{0}^{\omega},J_{-1}^{\omega}]^{T}$, and, as in Eq. (C5),

$$
\hat { \mathbf { r } } = \frac { \mathbf { r } } { | \mathbf { r } | } = 2 \sqrt { \frac { \pi } { 3 } } \left[ \begin{array}{l} { Y _ { 11 } ^{*} ( \hat { \mathbf { r } } ) } \\{ Y _ { 10 } ^{*} ( \hat { \mathbf { r } } ) } \\{ Y _ { 1 - 1 } ^{*} ( \hat { \mathbf { r } } ) } \end{array} \right] ,
$$

the result of the sum reads

$$
\begin{array}{rl} & { b _ { 11 } ^{\omega} = \frac { \sqrt { 3 } } { 2 \pi i } \int d ^{3} \mathbf { r } \ \left( J _ { 0 } ^{\omega} \hat { r } _ { 1 } - J _ { 1 } ^{\omega} \hat { r } _ { 0 } \right) j _ { 1 } ( k r ) , } \\& { b _ { 10 } ^{\omega} = \frac { \sqrt { 3 } } { 2 \pi i } \int d ^{3} \mathbf { r } \ \left( J _ { - 1 } ^{\omega} \hat { r } _ { 1 } - J _ { 1 } ^{\omega} \hat { r } _ { - 1 } \right) j _ { 1 } ( k r ) , } \\& { b _ { 1 - 1 } ^{\omega} = \frac { \sqrt { 3 } } { 2 \pi i } \int d ^{3} \mathbf { r } \ \left( J _ { - 1 } ^{\omega} \hat { r } _ { 0 } - J _ { 0 } ^{\omega} \hat { r } _ { - 1 } \right) j _ { 1 } ( k r ) . } \end{array}
$$

Considering the expression for the cross product in spherical coordinates [Eq. (C4)], we can finally write Eq. (19) as:

$$
\left[ \begin{array}{l} { b _ { 11 } ^{\omega} } \\{ b _ { 10 } ^{\omega} } \end{array} \right] = - \frac { \sqrt { 3 } } { 2 \pi } \int d ^{3} \mathbf { r } \, \hat { \mathbf { r } } \times \mathbf { J } _ { \omega } ( \mathbf { r } ) j _ { 1 } ( k r ) .
$$

The expressions for $[a_{11}^{\omega}, a_{10}^{\omega}, a_{1-1}^{\omega}]^{T}$ and $[c_{11}^{\omega}, c_{10}^{\omega}, c_{1-1}^{\omega}]^{T}$ can be obtained by similar, although more involved, procedures. We provide the derivations in App. D. The results read:

$$
\begin{array}{r} { \left[ \begin{array}{l} { a _ { 11 } ^{\omega} } \\{ a _ { 10 } ^{\omega} } \end{array} \right] = - \underbrace { \frac { 1 } { \pi \sqrt { 3 } } \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) j _ { 0 } ( k r ) } _ { \tilde { l } = 0 } } \\{ - \underbrace { \frac { 1 } { 2 \pi \sqrt { 3 } } \int d ^{3} \mathbf { r } \ \left\{ 3 \left[ \hat { \mathbf { r } } ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right] \hat { \mathbf { r } } - \mathbf { J } _ { \omega } ( \mathbf { r } ) \right\} j _ { 2 } ( k r ) } _ { \tilde { l } = 2 } , } \end{array}
$$

and

$$
\begin{array}{r} { \left[ \begin{array}{l} { c _ { 11 } ^{\omega} } \\{ c _ { 10 } ^{\omega} } \end{array} \right] = \underbrace { \frac { 1 } { \pi \sqrt { 6 } } \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) j _ { 0 } ( k r ) } _ { \tilde { l } = 0 } } \\{ - \underbrace { \frac { 1 } { \pi \sqrt { 6 } } \int d ^{3} \mathbf { r } \ \left\{ 3 \left[ \hat { \mathbf { r } } ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right] \hat { \mathbf { r } } - \mathbf { J } _ { \omega } ( \mathbf { r } ) \right\} j _ { 2 } ( k r ) } _ { \tilde { l } = 2 } , } \end{array}
$$

where the contributions coming from $\bar{l}=j-1=0$ and $\bar{l}=j+1=2$ are indicated. The dot product $\hat{\mathbf{r}}^{\dagger}\mathbf{J}_{\omega}(\mathbf{r})$ is simply equal to $\hat{\mathbf{r}}^{T}\mathbf{J}_{\omega}(\mathbf{r})$ in Cartesian coordinates².

Equation (20), Eq. (21), and Eq. (22) are exact. In particular they apply to a source distribution of any size. They are also simpler than the corresponding exact expressions obtained from Eq. (8) or Eq. (9). We note that Eqs. (20) to Eq. (22) should also be reachable from the coordinate space integrals of Eq. (8) or Eq. (9). Our route through momentum space explicitly exploits that the contributions to the $q_{jm}^{2}$ only come from the Fourier components of the source in the domain $|\mathbf{p}|=\omega/c$. This restriction is imposed in the exponential of Eq. (11) and determines the argument of the spherical Bessel functions $j_{l}(kr)$ in Eq. (14), which then appear in Eqs. (20),

Eq. (21), and Eq. (22). We can deduce that the spherical Bessel functions must be responsible for rejecting the $|\mathbf{p}| \neq \omega/c$ components present in $\mathbf{J}_{\omega}(\mathbf{r})$. We now provide a more formal proof of their role.

In the expression of $q_{jm}^{\omega}$ in Eq. (14), the dependence on the current density is contained in the integrals

$$
\int d ^{3} \mathbf { r } \, \mathbf { J } _ { \omega } ( \mathbf { r } ) Y _ { l m } ^{*} ( \hat { \mathbf { r } } ) j _ { l } ( k r ) .
$$

We then write $\mathbf{J}_{\omega}(\mathbf{r})$ as an inverse Fourier transform and expand its exponential $\exp (i\mathbf{p} \cdot \mathbf{r})$ as in Eq. (13), except that now $|\mathbf{p}|$ is not restricted to $\omega/c$. After rearranging the integrals we get:

$$
\sum _ { l , m } \frac { 4 \pi i ^{\tilde { l} } } { \sqrt { ( 2 \pi ) ^{3} } } \int d ^{3} { \bf p J } _ { \omega } ( { \bf p } ) Y _ { l m } ^{*} ( \hat { \bf p } ) \int d ^{3} { \bf r } Y _ { l m } ( \hat { \bf r } ) Y _ { l m } ^{*} ( \hat { \bf r } ) j _ { l } ( | { \bf p } | r ) j _ { l } ( k r ) \ .
$$

The shaded $d^{3}\mathbf{r}$ integral can be solved by splitting it into its radial and angular parts $\left(\int d^{3}\mathbf{r}=\int_{0}^{\infty}dr\ r^{2}\int d\hat{\mathbf{r}}\right)$. First, the angular part is solved through the orthonormality of the spherical harmonics, which forces $(\bar{l},\overline{m})=(l,m)$. The remaining radial integral has a formal solution as a radial Dirac delta distribution [17, Eq. (4.1)]

$$
\int d r r ^{2} j _ { l } ( | \mathbf { p } | r ) j _ { l } ( k r ) = \frac { \pi } { 2 k ^{2} } \delta ( | \mathbf { p } | - k ) ,
$$

which enforces the $|\mathbf{p}|=k=\omega/c$ restriction in Eq. (24), namely:

$$
\begin{array}{rl} & { \frac { 4 \pi i ^{l} } { \sqrt { ( 2 \pi ) ^{3} } } \int \, d ^{3} { \bf p } { \bf J } _ { \omega } ( { \bf p } ) Y _ { l m } ^{*} ( \hat { \bf p } ) \frac { \pi } { 2 k ^{2} } \delta ( | { \bf p } | - k ) = } \\& { \frac { 4 \pi i ^{l} } { \sqrt { ( 2 \pi ) ^{3} } } \int \, d \hat { \bf p } Y _ { l m } ^{*} ( \hat { \bf p } ) \int _ { 0 } ^{\infty} d p \, \hat { p } ^{2} { \bf J } _ { \omega } ( { \bf p } ) \frac { \pi } { 2 k ^{2} } \delta ( | { \bf p } | - k ) = } \\& { \frac { 1 } { k ^{2} } \sqrt { \frac { \pi } { 2 } } i ^{l} \int \, d \hat { \bf p } \, \hat { \bf \Phi } _ { \omega } ( \hat { \bf p } ) Y _ { l m } ^{*} ( \hat { \bf p } ) \, . } \end{array}
$$

The $j_{l}(kr)$ functions from Eq. (14) find their way into Eq. (25), and become one of the pieces needed to obtain the Dirac delta $\delta(|\mathbf{p}| - k)$ which filters out the $|\mathbf{p}| \neq \omega/c$ components of $\mathbf{J}_{\omega}(\mathbf{r})$.

# IV. ELECTROMAGNETICALLY SMALL SOURCE APPROXIMATION WITH INCREASING ACCURACY

We now make the small argument approximation to the spherical Bessel functions in Eqs. (20)-(22) and keep terms up to second order: $j_{0}(kr) \approx 1-(kr)^{2}/6$, $j_{1}(kr) \approx kr/3$ and $j_{2}(kr) \approx (kr)^{2}/15$. After grouping terms with

the same power of $k$ we obtain:

$$
\begin{array}{r} { \left[ \begin{array}{l} { b _ { 11 } ^{\omega} } \\{ b _ { 10 } ^{\omega} } \\{ b _ { 1 - 1 } ^{\omega} } \end{array} \right] \approx - \frac { 1 } { 2 \pi \sqrt { 3 } } k \int d ^{3} \mathbf { r } \ \mathbf { r } \times \mathbf { J } _ { \omega } ( \mathbf { r } ) , } \end{array}
$$

$$
\begin{array}{rl} & { \overbrace { \left[ \begin{array}{l} { a _ { 11 } ^{-} } \\{ a _ { 10 } ^{\omega} } \end{array} \right] } _ { l = 0 } \approx - \underbrace { \frac { 1 } { \pi \sqrt { 3 } } \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) } _ { l = 0 } } \\& { \underbrace { - \frac { 1 } { \pi \sqrt { 3 } } k ^{2} \int d ^{3} \mathbf { r } \ \frac { 1 } { 10 } \left\{ \left[ \mathbf { r } ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right] \mathbf { r } - 2 r ^{2} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right\} } _ { l = 0 , l = 2 } , } \\& { \underbrace { \left[ \begin{array}{l} { c _ { 11 } ^{\omega} } \\{ c _ { 10 } ^{\omega} } \end{array} \right] } _ { l = 0 } \approx \underbrace { \frac { 1 } { \pi \sqrt { 6 } } \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) } _ { l = 0 } } \\& { \underbrace { - \frac { 1 } { \pi } \sqrt { \frac { 2 } { 3 } } k ^{2} \int d ^{3} \mathbf { r } \ \frac { 1 } { 10 } \left\{ 2 \left[ \mathbf { r } ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right] \mathbf { r } + r ^{2} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right\} } _ { l = 0 , l = 2 } } \end{array}
$$

Equation (27), Eq. (28) and Eq. (29) are, respectively, the well known approximated magnetic, electric, and toroidal dipole moments of electromagnetically small current distributions. We note that the electric dipole contains contributions only from $\bar{l}=0$ while the toroidal dipole has contributions from $\bar{l}=0$ and $\bar{l}=2$.

The small argument approximation causes two kinds of inaccuracies. On the one hand, entire integral terms are neglected. For example, the toroidal term in Eq. (29) disappears in a lowest order approximation. On the other hand, some components with $|\mathbf{p}| \neq \omega/c$ will leak into the dipole moments. This happens because the approximated expressions of the spherical Bessel functions do not correspond to momentum space Dirac delta $\delta(|\mathbf{p}| - k)$.

Approximations with increasing accuracy are obtained in a straightforward way from the exact Eqs. (20) to Eq. (22). It is a matter of taking more terms in the expansions of the spherical Bessel functions. For example, the $(kr)^3$ correction to Eq. (27) reads

$$
\frac { \sqrt { 3 } k ^{3} } { 60 \pi } \int d ^{3} \mathbf { r } \ [ \mathbf { r } \times \mathbf { J } _ { \omega } ( \mathbf { r } ) ] \, r ^{2} ,
$$

the $(kr)^4$ correction to the total $a_{1m}^{\omega}$ in Eqs. reads

$$
\frac { k ^{4} } { 14 0 \pi \sqrt { 3 } } \int d ^{3} \mathbf { r } \, \left\{ \left[ \mathbf { r } ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right] \mathbf { r } - \frac { 3 } { 2 } \mathbf { J } _ { \omega } ( \mathbf { r } ) r ^{2} \right\} r ^{2} ,
$$

and the $(kr)^4$ correction to the total $c_{1m}^{\omega'}$ in Eqs. (30)-(31) reads

$$
\frac { k ^{4} } { 70 \pi \sqrt { 6 } } \int d ^{3} \mathbf { r } \, \left\{ \left[ \mathbf { r } ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right] \mathbf { r } + \frac { 1 } { 4 } \mathbf { J } _ { \omega } ( \mathbf { r } ) r ^{2} \right\} r ^{2} .
$$

The above corrections to $a_{1m}^{\omega}$ and $b_{1m}^{\omega}$ coincide up to normalization factors with the mean square radii in [15, App. C], where they are derived in a different way.

We now use our results to compute the magnetic dipole moment of a current distribution with a previously known analytical solution, verify that the result coincides, and compare it with two approximated solutions for electromagnetically small sources obtained from taking the first and the two first terms in the expansion of the spherical Bessel functions.

# V. EXAMPLE

Let us consider an infinitesimally thin circular loop of current with implicit time dependence $\exp(-i\omega t)$. The loop has radius $a$ and lies on the plane perpendicular to the $\hat{\mathbf{z}}$ axis (see the inset in Fig. 2). The expression for its current in spherical coordinates is

$$
\mathbf { J } _ { \omega } ( \mathbf { r } ) = \hat { \phi } I _ { 0 } \delta ( r - a ) \frac { 1 } { r } \delta ( \theta - \frac { \pi } { 2 } ) ,
$$

where $\hat{\phi} = [-\sin \phi, \cos \phi, 0]^T$, $\phi = \arctan(\frac{y}{x})$ and $\theta = \arccos(\frac{z}{r})$.

The exact value of its magnetic dipole moment is obtained after calculating the integral in Eq. (20):

$$
\mathbf { m } = \hat { \mathbf { z } } \sqrt { 3 } I _ { 0 } a j _ { 1 } ( k a ) .
$$

We obtain a first small source approximation by using Eq. (27) and a more accurate second one using the incremental correction in Eq. (32)

$$
\begin{array}{r} { \mathbf { m } _ { k a \ll 1 } ^{( 1 )} = \hat { \mathbf { z } } \sqrt { 3 } I _ { 0 } \frac { k a ^{2} } { 3 } , } \\{ \mathbf { m } _ { k a \ll 1 } ^{( 2 )} = \hat { \mathbf { z } } \sqrt { 3 } I _ { 0 } \frac { k a ^{2} } { 3 } \left[ 1 - ( k a ) ^{2} / 10 \right] . } \end{array}
$$

The same results are obtained by taking terms up to $ka$ and $(ka)^3$, respectively, in the Taylor series of $j_1(ka)$ in Eq. (36). This latter approach relies on the existence of an exact closed form solution and is hence not general.

The exact value of Eq. (36) coincides with the one calculated in [12, §13.3 p1881] up to a numerical factor that can be traced back to a different normalization. In this simple example, the relative error incurred due to the small source approximations is equal to the relative error incurred when approximating the first order spherical Bessel function. Figure 2 shows the relative errors incurred when taking only the first term in the expansion $[j_1(ka) \approx ka/3]$ and when taking the first two terms $\{j_1(ka) \approx (ka/3) \times [1 - (ka)^2/10]\}$. We see that, if we take only one term, a 10% relative error is incurred when

the diameter of the loop is approximately 30% of the wavelength. When taking two terms, the 10% relative error is reached when the diameter is approximately 70% of the wavelength. We note that in this example the current is concentrated in the most exterior region of the object. When this is not the case, e.g. in a homogeneous current distribution within a sphere of diameter $2a$, the relative errors should be smaller.

![](images/0dcdafec8c62263f9eda8c9cab28db7dbcaf669a7de25d8b7b242d8a54e80f88_38.jpg){width=38%} FIG. 2. Relative error in the magnetic dipole moment of an infinitesimally thin circular current loop of radius $a$ (shown in the inset) due to the small $2\pi a/\lambda_0$ approximation. Solid red line: Error due to taking only the first term in the small argument expansion of the spherical Bessel function in Eq. (20). Such first order gives the typical integral for the magnetic dipole moment of electromagnetically small sources [see Eq. (27)]. Dashed black line: Error due to taking the first two terms in the expansion, i.e. Eq. (27) plus Eq. (32).

# VI. RESULTS FOR HELICITY MULTIPOLES

There is some recent interest in the use of helicity for the study of interactions between matter and electromagnetic fields [18–22]. Due to its fundamental relationship with electromagnetic duality, the helicity formalism is also very useful when discussing dual symmetric systems [23, 24], e.g. Huggens surfaces [25, 26]. We now extend our results to the dipoles of well defined helicity.

Multipoles of well defined helicity are an alternative to the multipoles of well defined parity. The two sets are related by a change of basis, which we write for both the $q_{jm}^{\omega}$ coefficients and the $\mathbf{Q}_{jm}(\tilde{\mathbf{p}})$ functions:

$$
\begin{array}{rl} & { g _ { j m + } ^{\omega} = \frac { b _ { j m } ^{\omega} + a _ { j m } ^{\omega} } { \sqrt { 2 } } \iff \mathbf { G } _ { j m } ^{+} ( \hat { \mathbf { p } } ) = \frac { \mathbf { X } _ { j m } ( \hat { \mathbf { p } } ) + \mathbf { Z } _ { j m } ( \hat { \mathbf { p } } ) } { \sqrt { 2 } } = \frac { 1 + i \hat { \mathbf { p } } \times } { \sqrt { 2 } } \frac { \mathbf { L } \mathbf { Y } _ { j m } } { \sqrt { j ( j + 1 ) } } , } \\& { g _ { j m - } ^{\omega} = \frac { b _ { j m } ^{\omega} - a _ { j m } ^{\omega} } { \sqrt { 2 } } \iff \mathbf { G } _ { j m } ^{-} ( \hat { \mathbf { p } } ) = \frac { \mathbf { X } _ { j m } ( \hat { \mathbf { p } } ) - \mathbf { Z } _ { j m } ( \hat { \mathbf { p } } ) } { \sqrt { 2 } } = \frac { 1 - i \hat { \mathbf { p } } \times } { \sqrt { 2 } } \frac { \mathbf { L } \mathbf { Y } _ { j m } } { \sqrt { j ( j + 1 ) } } , } \\& { g _ { j m 0 } ^{\omega} = c _ { j m } ^{\omega} \iff \mathbf { G } _ { j m } ^{0} ( \hat { \mathbf { p } } ) = \mathbf { W } _ { j m } ( \hat { \mathbf { p } } ) = \hat { \mathbf { p } } Y _ { j m } , } \end{array}
$$

where $\mathbf{1}$ is the $3\times3$ unit matrix.

The $\mathbf{G}_{jm}^{\lambda}(\hat{\mathbf{p}})$ in Eq. (38) and the $\mathbf{Q}_{jm}(\hat{\mathbf{p}})$ have the same properties under rotations. They differ in their parity and polarization properties. Instead of eigenstates of parity, the $\mathbf{G}_{jm}^{\lambda}(\hat{\mathbf{p}})$ are eigenstates of the helicity operator with eigenvalue $\lambda$. This is obvious from the rightmost expressions in Eq. (38) since the helicity operator $\Lambda$ in the momentum representation is $i\hat{\mathbf{p}}\times$:

$$
\Lambda = \frac { \mathbf { J } \cdot \mathbf { P } } { | \mathbf { P } | } \rightarrow i \hat { \mathbf { p } } \times ,
$$

where $\mathbf{J}$ and $\mathbf{P}$ are the angular and linear momentum vector operators, respectively.

The two transverse families of this alternative basis, $\mathbf{G}_{jm}^{\pm}(\hat{\mathbf{p}})$, correspond to multipolar components $g_{jm\pm}^{\omega}$ that radiate fields of definite polarization handedness (helicity) $\lambda=\pm1$ [27, App. A].

The extension of our dipolar results to the helicity basis is straightforward. According to the third line of Eq. (38), the result for $\lambda=0$ is Eq. (22). The exact expressions for the transverse dipoles with helicity $\lambda=\pm1$ can be obtained using Eq. (20), Eq. (21) and Eq. (38):

The approximated expressions up to order $k^{2}$ are:

$$
\begin{array}{rl} { - 2 \pi \sqrt { 6 } \left[ \begin{array}{l} { g _ { 1 \lambda } ^{\omega} } \\{ g _ { 0 \lambda } ^{\omega} } \end{array} \right] = } & { } \\{ \int d ^{3} \mathbf { r } \left\{ k \mathbf { r } \times + \lambda \left[ 21 + \frac { k ^{2} } { 5 } \left( \mathbf { r } \mathbf { r } ^{\dagger} - 2 r ^{2} \mathbf { 1 } \right) \right] \right\} \mathbf { J } _ { \omega } ( \mathbf { r } ) . } & { } \end{array}
$$

# VII. CONCLUSION AND FUTURE WORK

In conclusion, we have obtained new exact expressions for the dipolar moments of a localized source distribution. These expressions are simpler than the ones reported to date. They are only marginally more complex than the typical integrals for the dipole moments of electromagnetically small sources and allow to easily obtain approximate expressions with increasing accuracy. Our results can be applied in the many areas where the dipole moments of electrical current sources are used.

In future work, we aim to obtain new exact expressions for general $j$-polar order and use them in applications like for instance in the study of the scattering properties of nanostructures.

# ACKNOWLEDGMENTS

I.F.-C. thanks Ms. Magda Felo for her help with the figures. S.N. acknowledges support by the Karlsruhe School of Optics & Photonics (KSOP). We acknowledge support by Deutsche Forschungsgemeinschaft and Open (40) Access Publishing Fund of Karlsruhe Institute of Technology. We also gratefully acknowledge financial support by the Deutsche Forschungsgemeinschaft (DFG) through

[1] L. D. Landau and E. Lifshitz. The Classical Theory of Fields. Butterworth-Heinemann (1975).

[2] J. D. Jackson. Classical Electrodynamics. Wiley (1998).

[3] C. Cohen-Tannoudji, J. Dupont-Roc, and G. Grynberg. Photons and Atoms: Introduction to Quantum Electrodynamics. Wiley (1989). Trans. of : Photons et atomes. InterEditions, 1987.

[4] D. P. Craig and T. Thirunamachandran. Molecular Quantum Electrodynamics: An Introduction to

Radiation-molecule Interactions. Academic Press (1984).

[5] J. D. Walecka. Theoretical Nuclear and Subnuclear Physics. World Scientific (2004).

[6] S. Mühlig, C. Menzel, C. Rockstuhl, and F. Lederer. Multipole analysis of meta-atoms. Metamaterials, 5, 2, 64 (2011).

[7] C. Rockstuhl, C. Menzel, S. Mühlig, J. Petschulat, C. Helgert, C. Etrich, A. Chipouline, T. Pertsch, and F. Lederer. Scattering properties of meta-atoms. Phys.

Rev. B, 83, 245119 (2011).

[8] P. Grahn, A. Shevchenko, and M. Kaivola. Electromagnetic multipole theory for optical nanomaterials. New J. Phys., 14, 9, 093033 (2012).

[9] F. B. Arango and A. F. Koenderink. Polarizability tensor retrieval for magnetic and plasmonic antenna design. New J. Phys., 15, 7, 073023 (2013).

[10] J. M. Blatt and V. F. Weisskopf. Theoretical Nuclear Physics. John Wiley & Sons Inc (1952).

[11] A. J. Devaney and E. Wolf. Multipole expansions and plane wave representations of the electromagnetic field. J. Math. Phys., 15, 2, 234 (1974).

[12] P. M. Morse and H. Feshbach. Methods of Theoretical Physics. McGraw-Hill and Kogakusha Book Companies (1953).

[13] I. Fernandez-Corbaton, S. Nanz, and C. Rockstuhl. On the dynamic toroidal multipoles. Under review. arXiv:1507.00755 (2015).

[14] V. M. Dubovik and A. A. Cheshkov. Multipole expansion in classical and quantum field theory and radiation. Sov. J. Part. Nucl., 5, 3, 318 (1974).

[15] E. Radescu and G. Vaman. Exact calculation of the angular momentum loss, recoil force, and radiation intensity for an arbitrary source in terms of electric, magnetic, and toroid multipoles. Phys. Rev. E, 65, 4, 046609 (2002).

[16] T. Kaelberer, V. A. Fedotov, N. Papasimakis, D. P. Tsai, and N. I. Zheludev. Toroidal Dipolar Response in a Metamaterial. Science, 330, 6010, 1510 (2010).

[17] R. Mehrem, J. Londergan, and M. Macfarlane. Analytic expressions for integrals of products of spherical Bessel functions. J. Phys. A: Math. Gen., 24, 7, 1435 (1991).

[18] M. K. Schmidt, J. Aizpurua, X. Zambrana-Puyalto, X. Vidal, G. Molina-Terriza, and J. J. Sáenz. Isotropically Polarized Speckle Patterns. Phys. Rev. Lett., 114, 113902 (2015).

[19] I. Fernandez-Corbaton, M. Fruhnert, and C. Rockstuhl. Dual and Chiral Objects for Optical Activity in General Scattering Directions. ACS Photonics, 2, 3, 376384 (2015).

[20] R. P. Cameron, S. M. Barnett, and A. M. Yao. Discriminatory optical force for chiral molecules. New J. Phys., 16, 1, 013020 (2014).

[21] N. Tischler, I. Fernandez-Corbaton, X. Zambrana-Puyalto, A. Minovich, X. Vidal, M. L. Juan, and G. Molina-Terriza. Experimental control of optical helicity in nanophotonics. Light Sci. Appl., 3, e183 (2014).

[22] K. Y. Bliokh and F. Nori. Characterizing optical chirality. Phys. Rev. A, 83, 2, 021803 (2011).

[23] I. Fernandez-Corbaton, X. Zambrana-Puyalto, N. Tischler, X. Vidal, M. L. Juan, and G. Molina-Terriza. Electromagnetic Duality Symmetry and Helicity Conservation for the Macroscopic Maxwell's Equations. Phys. Rev. Lett., 111, 6, 060401 (2013).

[24] I. Fernandez-Corbaton. Helicity and duality symmetry in light matter interactions: Theory and applications. Ph.D. thesis, Macquarie University (2014). arXiv: 1407.4432.

[25] C. Pfeiffer and A. Grbic. Metamaterial Huygens' Surfaces: Tailoring Wave Fronts with Reflectionless Sheets. Phys. Rev. Lett., 110, 197401 (2013).

[26] M. Decker, I. Staude, M. Falkner, J. Dominguez, D. N. Neshev, I. Brener, T. Pertsch, and Y. S. Kivshar. High-Efficiency Dielectric Huygens Surfaces. Adv. Opt. Mater. (2015).

[27] I. Fernandez-Corbaton, X. Zambrana-Puyalto, and G. Molina-Terriza. Helicity and angular momentum: A symmetry-based framework for the study of light-matter interactions. Phys. Rev. A, 86, 4, 042103 (2012).

[28] G. B. Arfken. Mathematical Methods for Physicists. Academic Press (1985).

[29] A. Messi. Quantum Mechanics. Dover (1999).

# Appendix A: Fields produced by time varying sources: Only Fourier components with $|\mathbf{p}|=\omega/c$ contribute

We consider a electric charge and current density distributions $\rho(\mathbf{r},t)$ and $\mathbf{J}(\mathbf{r},t)$ embedded in an isotropic and homogeneous medium with constant and real permittivity $\epsilon$ and permeability $\mu$. We assume them to be confined in space so that $\rho(\mathbf{r},t)=0$ and $\mathbf{J}(\mathbf{r},t)=0$ for $|\mathbf{r}|>R$. We consider the following Fourier decomposition:

$$
\begin{array}{rl} & { \rho ( \mathbf { r } , t ) = \mathcal { R } \left[ \int _ { 0 ^{+} } ^{\infty} \frac { d \omega } { \sqrt { 2 \pi } } \exp \left( - i \omega t \right) \rho _ { \omega } ( \mathbf { r } ) \right] } \\& { = \mathcal { R } \left[ \int _ { 0 ^{+} } ^{\infty} \frac { d \omega } { \sqrt { 2 \pi } } \exp \left( - i \omega t \right) \int \frac { d ^{3} \mathbf { p } } { \sqrt { ( 2 \pi ) ^{3} } } \rho _ { \omega } ( \mathbf { p } ) \exp \left( i \mathbf { p } \cdot \mathbf { r } \right) \right] , } \\& { \mathbf { J } ( \mathbf { r } , t ) = \mathcal { R } \left[ \int _ { 0 ^{+} } ^{\infty} \frac { d \omega } { \sqrt { 2 \pi } } \exp \left( - i \omega t \right) \mathbf { J } _ { \omega } ( \mathbf { r } ) \right] } \\& { = \mathcal { R } \left[ \int _ { 0 ^{+} } ^{\infty} \frac { d \omega } { \sqrt { 2 \pi } } \exp \left( - i \omega t \right) \int \frac { d ^{3} \mathbf { p } } { \sqrt { ( 2 \pi ) ^{3} } } \mathbf { J } _ { \omega } ( \mathbf { p } ) \exp \left( i \mathbf { p } \cdot \mathbf { r } \right) \right] . } \end{array}
$$

The lower limit of the integral in $d\omega$ excludes the static case $\omega=0$.

Devaney and Wolf [11] proved that, outside the source region, the transverse parts of the electromagnetic field produced by the source at frequency $\omega$ are determined by the transverse components of $\mathbf{J}_{\omega}(\mathbf{p})$ that meet $|\mathbf{p}|=\omega/c$, where $c=1/\sqrt{\epsilon\mu}$ is the speed of light in the medium.

We now provide a different proof which uses the potentials instead of the fields and shows the selection of the $|\mathbf{p}|=\omega/c$ components through the appearance of a radial delta distribution. We prove that the only parts of the sources that contribute to the scalar and vector potentials in the Lorenz gauge are those in the domain $|\mathbf{p}|=\omega/c$. The electric and magnetic fields obtained from the potentials are hence also determined by the components in the momentum space shell with radius $|\mathbf{p}|=\omega/c$, which means that the result is independent of the choice of gauge.

In the Lorenz gauge, and with implicit monochromatic $\exp\left(-i\omega t\right)$ dependence, the sources in Eq. (A1) generate the following scalar and vector potentials:

$$
\begin{array}{r} { \phi _ { \omega } ( \mathbf { r } ) = \frac { 1 } { \epsilon } \int d ^{3} \mathbf { r } ^{\prime} \rho _ { \omega } ( \mathbf { r } ^{\prime} ) \frac { \exp { ( i k | \mathbf { r } - \mathbf { r } ^{\prime} | ) } } { 4 \pi | \mathbf { r } - \mathbf { r } ^{\prime} | } } \\{ \mathbf { A } _ { \omega } ( \mathbf { r } ) = \mu \int d ^{3} \mathbf { r } ^{\prime} \ \mathbf { J } _ { \omega } ( \mathbf { r } ^{\prime} ) \frac { \exp { ( i k | \mathbf { r } - \mathbf { r } ^{\prime} | ) } } { 4 \pi | \mathbf { r } - \mathbf { r } ^{\prime} | } , } \end{array}
$$

where $k=\omega/c$.

Following Jackson's steps, we use the expansion of $\exp \left( i k \left| \mathbf { r } - \mathbf { r } ^ { \prime } \right| \right) / ( 4 \pi \left| \mathbf { r } - \mathbf { r } ^ { \prime } \right| )$ in [2, Eq. 9.98]

$$
\frac { \exp \left( i k | \mathbf { r } - \mathbf { r } ^{\prime} | \right) } { 4 \pi | \mathbf { r } - \mathbf { r } ^{\prime} | } = i k \sum _ { l = 0 } ^{\infty} h _ { l } ^{( 1 )} ( k r ) j _ { l } ( k r ^{\prime} ) \sum _ { m = - l } ^{m = l} Y _ { l m } ( \hat { \mathbf { r } } ) Y _ { l m } ^{*} ( \hat { \mathbf { r } } ^{\prime} )
$$

to get to [2, Eq. 9.11]:

$$
\begin{array}{rl} { \mathbf { A } _ { \omega } ( \mathbf { r } ) = } & { } \\& { i \mu k \sum _ { l , m } h _ { l } ^{( 1 )} ( k r ) Y _ { l m } ( \hat { \mathbf { r } } ) \underbrace { \int d ^{3} \mathbf { r } ^{\prime} \textbf { J } _ { \omega } ( \mathbf { r } ^{\prime} ) j _ { l } ( k r ^{\prime} ) Y _ { l m } ^{*} ( \hat { \mathbf { r } } ^{\prime} ) } _ { \mathbf { r } _ { l m } } , } \end{array}
$$

where $l$ and $m$ are integers, $h_{l}^{(1)}(\cdot)$ and $j_{l}(\cdot)$ are the $l$-th order spherical Hankel and Bessel functions, respectively, $\hat{\mathbf{f}}=\mathbf{r}/|\mathbf{r}|$, $\hat{\mathbf{r}}'=\mathbf{r}'/|\mathbf{r}'|$, $r=|\mathbf{r}|$, $r'=|\mathbf{r}'|$, and $Y_{jq}$ are the scalar spherical harmonics.

Let us now consider the integral labeled as $\mathbf{\Gamma}_{lm}$ in Eq. (A4) for a given term $(l,m)$. We use the inverse Fourier transform of $\mathbf{J}_{\omega}(\mathbf{r}^{\prime})$

$$
\mathbf { J } _ { \omega } ( \mathbf { r } ^{\prime} ) = \int \frac { d ^{3} \mathbf { p } } { \sqrt { ( 2 \pi ) ^{3} } } \mathbf { J } _ { \omega } ( \mathbf { p } ) \exp { ( i \mathbf { p } \cdot \mathbf { r } ^{\prime} ) } \, ,
$$

and the expansion of the exponential $\exp(i\mathbf{p}\cdot\mathbf{r}^{\prime})$ in spherical harmonics,

$$
\exp { ( i \mathbf { p } \cdot \mathbf { r } ^{\prime} ) } = ( 4 \pi ) \sum _ { l = 0 } ^{\infty} \sum _ { \overline { { { m } } } = - \overline { { { l } } } } ^{\overline { { { m} } } = \overline { { { l } } } } i ^{\overline { { { l} } } } Y _ { \overline { { { l } } } \overline { { { m } } } } ( \hat { \mathbf { r } } ^{\prime} ) Y _ { \overline { { { l } } } \overline { { { m } } } } ^{*} ( \hat { \mathbf { p } } ) j _ { \overline { { { l } } } } ( | \mathbf { p } | | \mathbf { r } ^{\prime} | ) ,
$$

to get

$$
\begin{array}{rl} { \frac { \Gamma _ { l m } } { 4 \pi } = } & { } \\& { \sum _ { l \overline { { { m } } } } \frac { \bar { I } } { i } \int d ^{3} \mathbf { r } ^{\prime} \int \frac { d ^{3} \mathbf { p } } { \sqrt { ( 2 \pi ) ^{3} } } \mathbf { J } _ { \omega } ( \mathbf { p } ) j _ { \bar { l } } ( | \mathbf { p } | r ^{\prime} ) j _ { l } ( k r ^{\prime} ) Y _ { \overline { { { l m } } } } ^{\ast} ( \hat { \mathbf { p } } ) Y _ { \overline { { { l m } } } } ^{\ast} ( \hat { \mathbf { r } } ^{\prime} ) Y _ { \overline { { { l m } } } } ^{\ast} ( \hat { \mathbf { r } } ^{\prime} ) . } \end{array}
$$

We stress that $\mathbf{J}_{\omega}(\mathbf{p})$ in Eq. (A5), and hence $\mathbf{J}_{\omega}(\mathbf{r}^{\prime})$ in Eq. (A4) and $\mathbf{\Gamma}_{lm}$ in Eq. (A7), may contain contributions from momenta $\mathbf{p}$ such that $|\mathbf{p}| \neq \omega / c$. The following steps show that these contributions are filtered out and that $\mathbf{A}_{\omega}(\mathbf{r})$ depends only on the components of $\mathbf{J}_{\omega}(\mathbf{p})$ with $|\mathbf{p}| = \omega / c$.

We take Eq. (A7), split the integral in $d^{3}\mathbf{r}^{\prime}$ into radial and angular parts $\left(\int d^{3}\mathbf{r}^{\prime}=\int_{0}^{\infty}d\mathbf{r}^{\prime}\,r^{\prime2}\int d\mathbf{\hat{r}}^{\prime}\right)$, and solve the angular part through the orthonormality of the spherical harmonics $\int d\mathbf{\hat{r}}^{\prime}Y_{l\overline{m}}(\mathbf{\hat{r}})Y_{l\overline{m}}^{*}(\mathbf{\hat{r}})=\delta_{l\overline{m}}\delta_{\overline{m}m}$. After this, the only term in the sum on $\overline{l}$ and $\overline{m}$ that does not vanish is the one meeting $\overline{l}=l$ and $\overline{m}=m$:

$$
\frac { \Gamma _ { l m } } { 4 \pi } = i ^{l} \int \frac { d ^{3} { \bf p } } { \sqrt { ( 2 \pi ) ^{3} } } { \bf J } _ { \omega } ( { \bf p } ) Y _ { l m } ^{*} ( { \hat { \bf p } } ) \int d r ^{\prime} ( r ^{\prime} ) ^{2} j _ { l } ( | { \bf p } | r ^{\prime} ) j _ { l } ( k r ^{\prime} ) \; .
$$

The crucial step is that the integral in the shaded box of Eq. (A8) has a formal solution as a radial Dirac delta distribution [17, Eq. 4.1]:

$$
\int d r ^{\prime} ( r ^{\prime} ) ^{2} j _ { i } ( | \mathbf { p } | r ^{\prime} ) j _ { i } ( k r ^{\prime} ) = \frac { \pi } { 2 k ^{2} } \delta ( | \mathbf { p } | - k ) .
$$

This $\delta(k-|\mathbf{p}|)$ term discards all momenta contributions from outside the spherical shell $|\mathbf{p}|=k=\omega/c$

in Eq. (A8). To show it explicitly, we split the integral in $d^{3}\mathbf{p}$ into radial ($p = |\mathbf{p}|$) and angular parts ($\int d^{3}\mathbf{p} = \int_{0}^{\infty} dp\,p^{2}\int d\hat{\mathbf{p}}$):

$$
\begin{array}{r} { \mathbf { \Gamma } _ { l m } = \frac { 4 \pi } { \sqrt { ( 2 \pi ) ^{3} } } i ^{l} \int d \hat { \mathbf { p } } \ Y _ { l m } ^{*} ( \hat { \mathbf { p } } ) \int d p \ p ^{2} \mathbf { J } _ { \omega } ( \mathbf { p } ) \frac { \pi } { 2 k ^{2} } \delta ( p - k ) = } \\{ \frac { i ^{l} } { \sqrt { 2 \pi } } \int d \hat { \mathbf { p } } \ \mathbf { J } _ { \omega } ( \mathbf { p } , | \mathbf { p } | = k ) Y _ { l m } ^{*} ( \hat { \mathbf { p } } ) . } \end{array}
$$

Since this conclusion holds for all values of $(l,m)$ in Eq. (A4), it follows that the vector potential is completely determined by $\mathbf{J}_{\omega}(\mathbf{p},|\mathbf{p}|=k)$, i.e., the components of $\mathbf{J}_{\omega}(\mathbf{p})$ on the momentum shell of radius $|\mathbf{p}|=\omega/c$.

The same conclusion is valid for the scalar potential $\phi_{\omega}(\mathbf{r})$ in Eq. (A2). This can be seen noting that none of the steps in the previous derivation needs the fact that $\mathbf{J}_{\omega}(\mathbf{r})$ is a vector. The same steps can be taken for the scalar charge density $\rho_{\omega}(\mathbf{r})$ which generates the scalar potential in Eq. (A2). Regarding its inverse Fourier transform

$$
\rho _ { \omega } ( \mathbf { r } ) = \int \frac { d ^{3} \mathbf { p } } { \sqrt { ( 2 \pi ) ^{3} } } \rho _ { \omega } ( \mathbf { p } ) \exp { ( i \mathbf { p } \cdot \mathbf { r } ) } \, ,
$$

the conclusion in this case is that $\phi_{\omega}(\mathbf{r})$ only depends on the momentum components of the charge density $\rho_{\omega}(\mathbf{p})$ in the momentum shell of radius $|\mathbf{p}|=\omega/c$.

Since both scalar and vector potentials ($\rho_{\omega}(\mathbf{r})$, $\mathbf{A}_{\omega}(\mathbf{r})$) depend only on the source Fourier components in the domain $|\mathbf{p}|=\omega/c$, the same will be true for the electric and magnetic fields computed from them:

$$
\mathbf { E } _ { \omega } ( \mathbf { r } ) = i \omega \mathbf { A } _ { \omega } ( \mathbf { r } ) - \nabla \phi _ { \omega } ( \mathbf { r } ) , \ \mathbf { B } _ { \omega } ( \mathbf { r } ) = \nabla \times \mathbf { A } _ { \omega } ( \mathbf { r } ) .
$$

It is hence clear that the conclusion is gauge independent. It is also clear that the derivation applies to both transverse and longitudinal components of the electromagnetic field, but the longitudinal electric field with $|\mathbf{p}|=\omega/c$ is zero outside the source region. This can be seen in [12, §13.3 p1875-1877], and in [13, App. C], where the cancellation is shown to be due to the continuity equation.

# Appendix B: One term in $b_{jm}^{\omega}$, two in $a_{jm}^{\omega}$ and $c_{jm}^{\omega}$

We show that, for $a_{jm}^{\vec{\omega}}$ and $c_{jm}^{\omega}$, only terms with $\vec{l}=j-1$ or $\vec{l}=j+1$ can be different from zero in Eq. (14), and that for $b_{jm}^{\omega}$, only $\vec{l}=j$ contributes. For this, we will write the momentum space integrals in the shaded area of Eq. (14) as integrals of triple products of spherical harmonics. These integrals have an exact expression involving a product of two 3j-Wigner symbols. The requirement that one of the 3j-Wigner symbols be non-null results in the aforementioned relationships between $j$ and $\vec{l}$.

Particularizing the shaded integrals in Eq. (14) to $\mathbf{W}_{jm}(\hat{\mathbf{p}})$ and $\mathbf{Z}_{jm}(\hat{\mathbf{p}})$

$$
\begin{array}{r} { \int d \hat { \mathbf { p } } \ \mathbf { W } _ { j m } ( \hat { \mathbf { p } } ) ^{\dagger} Y _ { \overline { { l } } \overline { { m } } } ( \hat { \mathbf { p } } ) = \int d \hat { \mathbf { p } } \ \left[ \hat { \mathbf { p } } Y _ { j m } ( \hat { \mathbf { p } } ) \right] ^{\dagger} Y _ { \overline { { l } } \overline { { m } } } ( \hat { \mathbf { p } } ) , } \\{ \int d \hat { \mathbf { p } } \ Z _ { j m } ^{\dagger} ( \hat { \mathbf { p } } ) Y _ { \overline { { l } } \overline { { m } } } ( \hat { \mathbf { p } } ) = \int d \hat { \mathbf { p } } \ \left[ i \hat { \mathbf { p } } \times \mathbf { X } _ { j m } ( \hat { \mathbf { p } } ) \right] ^{\dagger} Y _ { \overline { { l } } \overline { { m } } } ( \hat { \mathbf { p } } ) } \end{array}
$$

we find that each of their three components contains either one [in the $\mathbf{W}_{jm}(\hat{\mathbf{p}})$ case] or a sum of two [in the $\mathbf{Z}_{jm}(\hat{\mathbf{p}})$ case] triple products of spherical harmonics like $Y_{1p}^{*}Y_{jq}^{*}Y_{lr}$, which can be also written$^{3}$ as $(-1)^{p+q}Y_{1-p}Y_{j-q}^{*}Y_{lr}$. The result of the integral of the product of three spherical harmonics is [28, p. 700]

$$
\begin{array}{rl} & { \int d \Omega \ Y _ { l _ { 1 } m _ { 1 } } ( \Omega ) Y _ { l _ { 2 } m _ { 2 } } ( \Omega ) Y _ { l _ { 3 } m _ { 3 } } ( \Omega ) = } \\& { \sqrt { \frac { ( 2 l _ { 1 } + 1 ) ( 2 l _ { 2 } + 1 ) ( 2 l _ { 3 } + 1 ) } { 4 \pi } } \left( \begin{array}{lll} { l _ { 1 } } & { l _ { 2 } } & { l _ { 3 } } \\{ 0 } & { 0 } & { 0 } \end{array} \right) \left( \begin{array}{lll} { l _ { 1 } } & { l _ { 2 } } & { l _ { 3 } } \\{ m _ { 1 } } & { m _ { 2 } } & { m _ { 3 } } \end{array} \right) , } \end{array}
$$

<font color="red">【此段建议校对(This paragraph is recommended for proofreading)】</font>where $\begin{pmatrix} jj_{\text{d}}}} & &j_{\text{3}} \\ q_{_{\text{d}}_{\text{d}} & &q_{\text{3}}\end{pmatrix}$ is the 3j-Wigner symbol.$$

user只修正下面文本中\`...\`里的LaTeX语法错误，不改动文字、语义、标点，不补全答案，不随意加其他内容，直接返回修正后的文本：where $\left(\begin{array}{ll}j_{\text{d}} & a_{\text{d}} & j_{_{3} \\ q_{\text{_{\text{d}}}_{\text{f}} & a_{\text{d}} & q_{\text{3}}\end{array}\right)$ is the 3j-Wigner symbol.

In our case, we see from the right hand sides of Eq. (B1) that $j_{1}=1$ from $\hat{\mathbf{p}}$ [see Eq. (C5)], $j_{2}=j$ from $\mathbf{Z}_{jm}(\hat{\mathbf{p}})$ or $\mathbf{W}_{jm}(\hat{\mathbf{p}})$, and $j_{3}=l$ from $Y_{\overline{m}}(\hat{\mathbf{p}})$. We now consider some of the conditions for the first 3j-symbol in Eq. (B2)

$$
\left( \begin{array}{lll} { 1 } & { j } & { \bar { l } } \\{ 0 } & { 0 } & { 0 } \end{array} \right)
$$

to be different than zero. Namely [29, p. 1056]:

$$
| j _ { 1 } - j _ { 2 } | \leq j _ { 3 } \leq j _ { 1 } + j _ { 2 } \implies | 1 - j | \leq \bar { l } \leq j + 1
$$

which, if $j>0$ restricts $\bar{l}$ to be $j-1$, $j$ or $j+1$ and, when $j=0$ in the longitudinal case, forces $\bar{l}=1$. Furthermore, because of the zeros in Eq. (B3), $1+j+\bar{l}$ must be an integer multiple of 2, which then forbids $\bar{l}=j$ when $j>0$. All together we obtain for the $\mathbf{W}_{jm}(\hat{\mathbf{p}})$ and $\mathbf{Z}_{jm}(\hat{\mathbf{p}})$ cases the restrictions:

$$
\begin{array}{r} { \bar { l } = j - 1 \mathrm { ~ o r ~ } j + 1  \mathrm { i f ~ } j > 0 , } \\{ \bar { l } = 1  \mathrm { i f ~ } j = 0 . } \end{array}
$$

In the $\mathbf{X}_{jm}(\hat{\mathbf{p}})$ case, the integrals in the three components of

$$
\int d \hat { \mathbf { p } } \ \mathbf { X } _ { j m } ^{\dagger} ( \hat { \mathbf { p } } ) Y _ { \overline { { { l m } } } } ( \hat { \mathbf { p } } )
$$

contain a product of two spherical harmonics, but the third one can always be assumed to be the constant $1=\sqrt{4\pi Y_{00}}$. In this case the restriction of Eq. (B4) forces $\bar{l}=j$.

$$
| 0 - j | \leq \bar { l } \leq j + 0 \implies \bar { l } = j .
$$

# Appendix C: Auxiliary expressions in the spherical vector basis

We write a vector $\mathbf{a}$ in the spherical vector basis as:

$$
\mathbf { a } = a _ { 1 } \hat { \mathbf { e } } _ { 1 } + a _ { 0 } \hat { \mathbf { e } } _ { 0 } + a _ { - 1 } \hat { \mathbf { e } } _ { - 1 } ,
$$

with

$$
\begin{array}{r} { \hat { \mathbf { e } } _ { 1 } = - \frac { \hat { \mathbf { x } } + i \hat { \mathbf { y } } } { \sqrt { 2 } } } \\{ \hat { \mathbf { e } } _ { 0 } = \hat { \mathbf { z } } } \\{ \hat { \mathbf { e } } _ { - 1 } = \frac { \hat { \mathbf { x } } - i \hat { \mathbf { y } } } { \sqrt { 2 } } . } \end{array}
$$

This choice of basis induces the following relationships between the Cartesian and spherical coordinates of $\mathbf{a}$ in the spherical and Cartesian basis:

$$
\begin{array}{rl} { \left[ \begin{array}{l} { a _ { 1 } } \\{ a _ { 0 } } \\{ a _ { - 1 } } \end{array} \right] } & { = \left[ \begin{array}{lll} { \frac { - 1 } { \sqrt { 2 } } } & { \frac { i } { \sqrt { 2 } } } & { 0 } \\{ 0 } & { 0 } & { 1 } \\{ \frac { 1 } { \sqrt { 2 } } } & { \frac { i } { \sqrt { 2 } } } & { 0 } \end{array} \right] \left[ \begin{array}{l} { a _ { x } } \\{ a _ { y } } \\{ a _ { z } } \end{array} \right] , \left[ \begin{array}{l} { a _ { x } } \\{ a _ { y } } \\{ a _ { z } } \end{array} \right] = \left[ \begin{array}{lll} { \frac { - 1 } { \sqrt { 2 } } } & { 0 } & { \frac { 1 } { \sqrt { 2 } } } \\{ \frac { - i } { \sqrt { 2 } } } & { 0 } & { \frac { i } { \sqrt { 2 } } } \\{ 0 } & { 1 } & { 0 } \end{array} \right] \left[ \begin{array}{l} { a _ { 1 } } \\{ a _ { 0 } } \\{ a _ { - 1 } } \end{array} \right] } \end{array}
$$

In the spherical basis, the components of the cross product of two vectors are $^{4}$:

$$
\mathbf { a } \times \mathbf { b } = i \left[ \begin{array}{l} { a _ { 1 } b _ { 0 } - a _ { 0 } b _ { 1 } } \\{ a _ { 1 } b _ { - 1 } - a _ { - 1 } b _ { 1 } } \\{ a _ { 0 } b _ { - 1 } - a _ { - 1 } b _ { 0 } } \end{array} \right] .
$$

Let us now write some explicit expressions for $\hat{\mathbf{p}}$ and $\mathbf{X}_{jm}(\hat{\mathbf{p}})$ that we use in the text.

$$
\hat { \mathbf { p } } = \frac { \mathbf { p } } { | \mathbf { p } | } = \left[ \begin{array}{l} { \hat { p } _ { 1 } } \\{ \hat { p } _ { 0 } } \\{ \hat { p } _ { - 1 } } \end{array} \right] = 2 \sqrt { \frac { \pi } { 3 } } \left[ \begin{array}{l} { - Y _ { 1 - 1 } } \\{ Y _ { 10 } } \\{ - Y _ { 11 } } \end{array} \right] = 2 \sqrt { \frac { \pi } { 3 } } \left[ \begin{array}{l} { Y _ { 11 } ^{*} } \\{ Y _ { 10 } ^{*} } \\{ Y _ { 1 - 1 } ^{*} } \end{array} \right] _ { C ^{\mathrm { T} } } ,
$$

$$
\mathbf { X } _ { j m } ( \hat { \mathbf { p } } ) = \frac { 1 } { \sqrt { j ( j + 1 ) } } \left[ \begin{array}{c} { { - \sqrt { \frac { j ( j + 1 ) - m ( m - 1 ) } { 2 } } Y _ { j ( m - 1 ) } ( \hat { \mathbf { p } } ) } } \\{ { m Y _ { j m } ( \hat { \mathbf { p } } ) } } \\{ { \sqrt { \frac { j ( j + 1 ) - m ( m + 1 ) } { 2 } } Y _ { j ( m + 1 ) } ( \hat { \mathbf { p } } ) } } \end{array} \right] .
$$

Equation (C5) follows Eq. (C3), the expressions of $Y_{1m}$ in Cartesian coordinates and the property $Y_{lq}^{*}=(-1)^{q}Y_{l-q}$. Equation (C6) follows from the definition of

$\mathbf{X}_{jm}$ in Eq. (2) and the expression of the angular momentum vector operator $\mathbf{L}$ in spherical coordinates

$$
\mathbf { L } = \left[ \begin{array}{l} { \frac { - L _ { x } + i L _ { y } } { \sqrt { 2 } } } \\{ L _ { z } } \\{ \frac { L _ { x } + i L _ { y } } { \sqrt { 2 } } } \end{array} \right] = \left[ \begin{array}{l} { - \frac { L _ { d o w n } } { \sqrt { 2 } } } \\{ L _ { 0 } } \\{ \frac { L _ { u n } } { \sqrt { 2 } } } \end{array} \right] ,
$$

where $L_{\mathrm{up}}=L_{x}+iL_{y}$ and $L_{\mathrm{down}}=L_{x}-iL_{y}$ are the angular momentum ladder operators

$$
\begin{array}{r} { L _ { \mathrm { u p } } Y _ { j m } = \left\{ \begin{array}{ll} { \sqrt { j ( j + 1 ) - m ( m + 1 ) } Y _ { j ( m + 1 ) } } & { \mathrm { i f ~ } | m + 1 | \leq j } \\{ 0 } & { \mathrm { e l s e } } \end{array} \right. , } \\{ L _ { \mathrm { d o w n } } Y _ { j m } = \left\{ \begin{array}{ll} { \sqrt { j ( j + 1 ) - m ( m - 1 ) } Y _ { j ( m - 1 ) } } & { \mathrm { i f ~ } | m - 1 | \leq j } \\{ 0 } & { \mathrm { e l s e } } \end{array} \right. . } \end{array}
$$

Appendix D: Expression of selected $q_{jm}^{\omega'}$ tensors as spatial integrals

# 1. Case $a_{1m}$

As shown in App. B only $\bar{l}=0$ and $\bar{l}=2$ can have non zero contributions to $a_{1m}$. That is

$$
a _ { 1 m } ^{\omega} = a _ { 1 m } ^{\omega} \stackrel { \bar { l } = 0 } { \longrightarrow } a _ { 1 m } ^{\omega} \stackrel { \bar { l } = 2 } { \longrightarrow } .
$$

We start with $\bar{l}=0$. From Eq. (14), and since $Y_{00}=1/\sqrt{4\pi}$:

$$
a _ { 1 m } ^{\bar { l} = 0 } = \frac { 1 } { \sqrt { ( 2 \pi ) ^{3} } } \int d \hat { \mathbf { p } } \ \mathbf { Z } _ { 1 m } ^{\dagger} ( \hat { \mathbf { p } } ) \ \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) j _ { 0 } ( k r ) .
$$

The explicit expressions for $\mathbf{Z}_{1m} = i\hat{\mathbf{p}} \times \mathbf{X}_{1m}$ are

$$
\begin{array}{rl} & { m = 1 \rightarrow \ i \hat { \mathbf { p } } \times \mathbf { X } _ { 11 } ( \hat { \mathbf { p } } ) = - \sqrt { \frac { 2 \pi } { 3 } } \left[ \begin{array}{l} { Y _ { 10 } ^{2} - Y _ { 11 } Y _ { 1 - 1 } } \\{ - Y _ { 11 } Y _ { 10 } } \end{array} \right] \, , } \\& { m = 0 \rightarrow \ i \hat { \mathbf { p } } \times \mathbf { X } _ { 10 } ( \hat { \mathbf { p } } ) = - \sqrt { \frac { 2 \pi } { 3 } } \left[ \begin{array}{l} { Y _ { 10 } Y _ { 1 - 1 } } \\{ - 2 Y _ { 11 } Y _ { 1 - 1 } } \\{ Y _ { 10 } Y _ { 11 } } \end{array} \right] \, , } \\& { m = - 1 \rightarrow \ i \hat { \mathbf { p } } \times \mathbf { X } _ { 1 - 1 } ( \hat { \mathbf { p } } ) = - \sqrt { \frac { 2 \pi } { 3 } } \left[ \begin{array}{l} { Y _ { 10 } ^{2} } \\{ - Y _ { 10 } Y _ { 1 - 1 } } \\{ Y _ { 10 } ^{2} - Y _ { 11 } Y _ { 1 - 1 } } \end{array} \right] \, . } \end{array}
$$

The relationship $Y_{lq}^{*}=(-1)^{q}Y_{l-q}$, and the orthonormality of the spherical harmonics allow us to solve the momentum space integrals in the shaded area of Eq. (D2), and immediately reach

$$
\left[ \begin{array}{l} { a _ { 11 } ^{\omega} } \\{ a _ { 1 - 1 } ^{\omega} } \end{array} \right] ^{\bar { l} = 0 } = - \frac { 1 } { \pi \sqrt { 3 } } \int d ^{3} \mathbf { r } \, \mathbf { J } _ { \omega } ( \mathbf { r } ) j _ { 0 } ( k r ) .
$$

In the $\bar{l}=2$ case

$$
\begin{array}{rl} { \frac { \sqrt { ( 2 \pi ) ^{3} } } { 4 \pi } a _ { 1 m } ^{\bar { I} = 2 } = } & { { } } \\{ - \sum _ { \overline { { { m } } } = - 2 } ^{\overline { { { m} } } = 2 } \int d \hat { \mathbf { p } } \, \mathbf { Z } _ { 1 m } ^{\dagger} ( \hat { \mathbf { p } } ) Y _ { 2 \overline { { { m } } } } \int d ^{3} \mathbf { r } \, \mathbf { J } _ { \omega } ( \mathbf { r } ) Y _ { 2 \overline { { { m } } } } ^{*} j _ { 2 } ( k r ) , } & { { } } \end{array}
$$

the shaded momentum space integrals contain triple products of spherical harmonics and can be solved using

$$
\begin{array}{rl} & { \int d \hat { \mathbf { p } } Y _ { l _ { 1 } m _ { 1 } } ( \hat { \mathbf { p } } ) Y _ { l _ { 2 } m _ { 2 } } ( \hat { \mathbf { p } } ) Y _ { l _ { 3 } m _ { 3 } } ( \hat { \mathbf { p } } ) = } \\& { \sqrt { \frac { ( 2 l _ { 1 } + 1 ) ( 2 l _ { 2 } + 1 ) ( 2 l _ { 3 } + 1 ) } { 4 \pi } } \left( \begin{array}{lll} { l _ { 1 } } & { l _ { 2 } } & { l _ { 3 } } \\{ 0 } & { 0 } & { 0 } \end{array} \right) \left( \begin{array}{lll} { l _ { 1 } } & { l _ { 2 } } & { l _ { 3 } } \\{ m _ { 1 } } & { m _ { 2 } } & { m _ { 3 } } \end{array} \right) , } \end{array}
$$

<font color="red">【此段建议校对(This paragraph is recommended for proofreading)】</font>where $\begin{pmatrix} jj_{\text{d}}}} & &j_{\text{3}} \\ q_{\text{d}} & &q_{\text{3}}\end{pmatrix}$}$$ is the 3j-Wigner symbol.

They result in five vectors for each $m$ case, which we list here as row vectors. From top to bottom, the row vectors correspond to $\overline{m}=2,1,0,-1,-2$:

$$
\begin{aligned}(\begin{array}{ccc}0&0&\sqrt{6}\end{array})\\m=1\:\to\:\frac{-1}{\sqrt{30}}(\begin{array}{ccc}0&-\sqrt{3}&0\end{array})\\m=1\:\to\:\frac{-1}{\sqrt{30}}(\begin{array}{ccc}1&0&0\\0&0&0\end{array})\\(\begin{array}{ccc}0&0&0\\0&0&0\end{array})\\m=0\:\to\:\frac{-1}{\sqrt{30}}(\begin{array}{ccc}0&0&\sqrt{3}\end{array})\\(\begin{array}{ccc}\sqrt{3}&0&0\end{array})\\(\begin{array}{ccc}0&0&0\\0&0&0\end{array})\\n=-1\:\to\:\frac{-1}{\sqrt{30}}(\begin{array}{ccc}0&0&1\end{array})\\(\begin{array}{ccc}0&-\sqrt{3}&0\end{array})\\(\begin{array}{ccc}\sqrt{6}&0&0\end{array})\end{aligned}
$$

The summation in $\overline{m}$ in Eq. (D5) can now be done. With $\mathbf{J}_{\omega}(\mathbf{r})=[J_{1}^{\omega},J_{0}^{\omega},J_{-1}^{\omega}]^{T}$, and $Y_{2m}^{*}=(-1)^{m}Y_{2-m}$, it reads

$$
\begin{array}{rl} & { a _ { 11 } ^{\omega} \bar { l } = 2 = \frac { 1 } { \sqrt { ( 2 \pi ) ^{3} } } \frac { 4 \pi } { \sqrt { 30 } } \int d ^{3} { \bf r } \, \left( \sqrt { 6 } J _ { - 1 } ^{\omega} Y _ { 2 - 2 } + \sqrt { 3 } J _ { 0 } ^{\omega} Y _ { 2 - 1 } + J _ { 1 } ^{\omega} Y _ { 20 } \right) j _ { 2 } ( k r ) , } \\& { a _ { 10 } ^{\omega} \bar { l } = 2 = \frac { 1 } { \sqrt { ( 2 \pi ) ^{3} } } \frac { 4 \pi } { \sqrt { 30 } } \int d ^{3} { \bf r } \, \left( - \sqrt { 3 } J _ { - 1 } ^{\omega} Y _ { 2 - 1 } - 2 J _ { 0 } ^{\omega} Y _ { 20 } - \sqrt { 3 } J _ { 1 } ^{\omega} Y _ { 21 } \right) j _ { 2 } ( k r ) , } \\& { a _ { 1 - 1 } ^{\omega} \bar { l } = 2 = \frac { 1 } { \sqrt { ( 2 \pi ) ^{3} } } \frac { 4 \pi } { \sqrt { 30 } } \int d ^{3} { \bf r } \, \left( J _ { - 1 } ^{\omega} Y _ { 20 } + \sqrt { 3 } J _ { 0 } ^{\omega} Y _ { 21 } + \sqrt { 6 } J _ { 1 } ^{\omega} Y _ { 22 } \right) j _ { 2 } ( k r ) . } \end{array}
$$

We now use the following relationships:

$$
\begin{array}{r} { Y _ { 22 } = \sqrt { \frac { 10 \pi } { 3 } } Y _ { 11 } ^{2} , \ Y _ { 21 } = \sqrt { \frac { 20 \pi } { 3 } } Y _ { 10 } Y _ { 11 } } \\{ Y _ { 20 } = \sqrt { 5 \pi } \left( Y _ { 10 } ^{2} - \frac { 1 } { 4 \pi } \right) } \\{ Y _ { 2 - 2 } = \sqrt { \frac { 10 \pi } { 3 } } Y _ { 1 - 1 } ^{2} , \ Y _ { 2 - 1 } = \sqrt { \frac { 20 \pi } { 3 } } Y _ { 10 } Y _ { 1 - 1 } , } \end{array}
$$

which we substitute in Eq. (D8) and get

$$
\begin{array}{rl} & { a _ { 11 } ^{\omega} { } ^{\bar { l} = 2 } = \frac { 2 } { \sqrt { 3 } } \int d ^{3} \mathbf { r } \, \left[ Y _ { 1 - 1 } \, \left( J _ { - 1 } ^{\omega} Y _ { 1 - 1 } + J _ { 0 } ^{\omega} Y _ { 10 } \right) \, + \frac { J _ { 1 } ^{\omega} } { 2 } \left( Y _ { 10 } ^{2} - \frac { 1 } { 4 \pi } \right) \right] j _ { 2 } ( k r ) , } \\& { a _ { 10 } ^{\omega} { } ^{\bar { l} = 2 } = \frac { - 2 } { \sqrt { 3 } } \int d ^{3} \mathbf { r } \, \left[ Y _ { 10 } \, \left( J _ { - 1 } ^{\omega} Y _ { 1 - 1 } + J _ { 1 } ^{\omega} Y _ { 11 } \right) \, + J _ { 0 } ^{\omega} \left( Y _ { 10 } ^{2} - \frac { 1 } { 4 \pi } \right) \right] j _ { 2 } ( k r ) , } \\& { a _ { 1 - 1 } ^{\omega} { } ^{\bar { l} = 2 } = \frac { 2 } { \sqrt { 3 } } \int d ^{3} \mathbf { r } \, \left[ Y _ { 11 } \, \left( J _ { 0 } ^{\omega} Y _ { 10 } + J _ { 1 } ^{\omega} Y _ { 11 } \right) \, + \frac { J _ { - 1 } ^{\omega} } { 2 } \left( Y _ { 10 } ^{2} - \frac { 1 } { 4 \pi } \right) \right] j _ { 2 } ( k r ) . } \end{array}
$$

The expressions in the shaded areas of Eq. (D10) can be completed to $Y_{11}J_{1}^{\omega}+Y_{10}J_{0}^{\omega}+Y_{1-1}J_{-1}^{\omega}$ using terms to their right. In the case of the $a_{10}^{\omega}$ $l=2$ the completion is straightforward. For the other two cases one uses that

$$
\frac { 3 } { 4 \pi } = | Y _ { 10 } | ^{2} + | Y _ { 11 } | ^{2} + | Y _ { 1 - 1 } | ^{2} \implies Y _ { 10 } ^{2} - \frac { 1 } { 4 \pi } = \frac { 1 } { 2 \pi } + 2 Y _ { 11 } Y _ { 1 - 1 } .
$$

Finally, noting that

$$
Y _ { 11 } J _ { 1 } ^{\omega} + Y _ { 10 } J _ { 0 } ^{\omega} + Y _ { 1 - 1 } J _ { - 1 } ^{\omega} = \frac { 1 } { 2 } \sqrt { \frac { 3 } { \pi } } \left[ \hat { \mathbf { r } } ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right] ,
$$

we reach the final result

$$
\left[ \begin{array}{l} { a _ { 11 } ^{\omega} } \\{ a _ { 10 } ^{\omega} } \\{ a _ { 1 - 1 } ^{\omega} } \end{array} \right] ^{\tilde { l} = 2 } = - \frac { 1 } { 2 \pi \sqrt { 3 } } \int d ^{3} \mathbf { r } \ \left\{ 3 \left[ \hat { \mathbf { r } } ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right] \hat { \mathbf { r } } - \mathbf { J } _ { \omega } ( \mathbf { r } ) \right\} \dot { j } _ { 2 } ( k r ) .
$$

The sum of the two contributions can be manipulated with the aid of the recursion relations between spherical Bessel functions:

$$
\begin{array}{r} { \frac { 2 l + 1 } { x } j _ { l } ( x ) = j _ { l - 1 } ( x ) + j _ { l + 1 } ( x ) , } \\{ ( 2 l + 1 ) \frac { d } { d x } j _ { l } ( x ) = l _ { l } j _ { l - 1 } ( x ) - ( l + 1 ) j _ { l + 1 } ( x ) , } \end{array}
$$

to get, with the definitions $\mathbf{J}_{\omega}^{r}(\mathbf{r})=\left[\hat{\mathbf{r}}^{\dagger}\mathbf{J}_{\omega}(\mathbf{r})\right]\hat{\mathbf{r}}$ and $\mathbf{J}_{\omega}^{t}(\mathbf{r})=\mathbf{J}_{\omega}(\mathbf{r})-\mathbf{J}_{\omega}^{t}(\mathbf{r})$,

$$
\begin{array}{r} { \left[ \begin{array}{l} { a _ { 11 } ^{\omega} } \\{ a _ { 10 } ^{\omega} } \end{array} \right] = - \frac { 1 } { 2 \pi \sqrt { 3 } } \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ^{r} ( \mathbf { r } ) \frac { 6 } { k r } j _ { 1 } ( k r ) } \\{ - \frac { 1 } { 2 \pi \sqrt { 3 } } \int d ^{3} \mathbf { r } \ 3 \mathbf { J } _ { \omega } ^{t} ( \mathbf { r } ) \left( \frac { 1 } { k r } + \frac { d } { d ( k r ) } \right) j _ { 1 } ( k r ) . } \end{array}
$$

# 2. Case $c_{00}$

In the $j=0$ case the contribution corresponding to $\bar{l}=j-1=-1$ does not exist (see App. B), so the only contribution comes from $\bar{l}=1$:

$$
\begin{array}{rl} & { i \sqrt { \frac { \pi } { 2 } } c _ { 00 } = \frac { \overline { { m } } = 1 } { \sum _ { \overline { { m } } = - 1 } ^{\overline { { m} } = 1 } } \int d \hat { \mathbf { p } } \ \mathbf { W } _ { 00 } ^{\dagger} ( \hat { \mathbf { p } } ) \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) Y _ { 1 \overline { { m } } } ^{*} j _ { 1 } ( k r ) } \\& { = \sum _ { \overline { { m } } = - 1 } ^{\overline { { m} } = 1 } \int d \hat { \mathbf { p } } \ \left( \hat { \mathbf { p } } \right) ^{\dagger} Y _ { 1 \overline { { m } } } ( \hat { \mathbf { p } } ) \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) Y _ { 1 \overline { { m } } } ^{*} j _ { 1 } ( k r ) . } \end{array}
$$

The integrals in the shaded area are conveniently solved using Eq. (C5) and the orthonormality of the spherical harmonics. After the sum in $\overline{m}$ we get:

$$
\begin{array}{r} { i \sqrt { \frac { \pi } { 2 } } c _ { 00 } = \int d ^{3} \mathbf { r } \ 2 \sqrt { \frac { \pi } { 3 } } \left( - J _ { - 1 } ^{\omega} Y _ { 11 } ^{*} + J _ { 0 } ^{\omega} Y _ { 10 } ^{*} - J _ { 1 } ^{\omega} Y _ { 1 - 1 } ^{*} \right) j _ { 1 } ( k r ) } \\{ = \int d ^{3} \mathbf { r } \ \left[ \hat { \mathbf { r } } ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right] j _ { 1 } ( k r ) . } \end{array}
$$

The first term in a small $kr$ expansion of $c_{00}$ will be of order $k$:

$$
c _ { 00 } \approx - i \sqrt { \frac { 2 } { \pi } } \frac { k } { 3 } \int d ^{3} \mathbf { r } \ \left[ \mathbf { r } ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right] .
$$

# 3. Case $c_{1m}$

As in Sec. D 1, we split the two contributions:

$$
c _ { 1 m } ^{\omega} = c _ { 1 m } ^{\omega} \bar { l } = 0 + c _ { 1 m } ^{\omega} \bar { l } = 2 \, .
$$

For $\bar{l}=0$, and recalling that $Y_{00}=1/\sqrt{4\pi}$:

$$
\begin{array}{r} { \mathrm { c } _ { 1 m } ^{\tilde { l} = 0 } = \frac { 4 \pi } { \sqrt { ( 2 \pi ) ^{3} } } \int d \hat { \mathbf { p } } \ \mathbf { W } _ { 1 m } ( \hat { \mathbf { p } } ) ^{\dagger} \frac { 1 } { \sqrt { 4 \pi } } \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) \frac { 1 } { \sqrt { 4 \pi } } j _ { 0 } ( k r ) , } \\{ = \frac { 1 } { \sqrt { ( 2 \pi ) ^{3} } } \int d \hat { \mathbf { p } } \ \left[ \hat { \mathbf { p } } Y _ { 1 m } ( \hat { \mathbf { p } } ) \right] ^{\dagger} \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) j _ { 0 } ( k r ) . } \end{array}
$$

The result of the integrals in the shaded area above is:

$$
m = 1 : 2 \sqrt { \frac { \pi } { 3 } } \left[ \begin{array}{l} { 1 } \\{ 0 } \\{ 0 } \end{array} \right] , \ m = 0 : \ 2 \sqrt { \frac { \pi } { 3 } } \left[ \begin{array}{l} { 0 } \\{ 1 } \\{ 0 } \end{array} \right] , \ m = - 1 : \ 2 \sqrt { \frac { \pi } { 3 } } \left[ \begin{array}{l} { 0 } \\{ 0 } \\{ 1 } \end{array} \right] .
$$

With which we reach:

$$
\left[ \begin{array}{l} { c _ { 11 } ^{\omega} } \\{ c _ { 10 } ^{\omega} } \\{ c _ { 1 - 1 } ^{\omega} } \end{array} \right] ^{\bar { l} = 0 } = \frac { 1 } { \pi \sqrt { 6 } } \int d ^{3} \mathbf { r } \, \mathbf { J } _ { \omega } ( \mathbf { r } ) j _ { 0 } ( k r ) .
$$

$$
\mathrm { F o r } \, \bar { l } = 2 \colon
$$

$$
\begin{array}{rl} { c _ { 1 m } ^{\tilde { l} = 2 } = } & { } \\{ \frac { - 4 \pi } { \sqrt { ( 2 \pi ) ^{3} } } \sum _ { m = - 2 } ^{\overline { { m} } = 2 } \int d \mathbf { \hat { p } } \ [ \hat { \mathbf { p } } Y _ { 1 m } ( \hat { \mathbf { p } } ) ] ^{\dagger} Y _ { 2 \overline { { m } } } \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) Y _ { 2 \overline { { m } } } ^{*} j _ { 2 } ( k r ) , } & { } \end{array}
$$

the shaded momentum space integrals contain triple products of spherical harmonics and can be solved using Eq. (D6). They result in five vectors for each $m$ case, which we list here as row vectors. From top to bottom, the row vectors corresponds to $\overline{m}=2,1,0,-1,-2$:

$$
\begin{array}{rl} { m = 1 \rightarrow \frac { \left( \begin{array}{lll} { 0 } & { 0 } & { \sqrt { 6 } } \\{ 0 } & { - \sqrt { 3 } } & { 0 } \end{array} \right) } { \sqrt { 15 } } \left( \begin{array}{lll} { 1 } & { 0 } & { 0 } \\{ 0 } & { 0 } & { 0 } \end{array} \right) } & { } \\{ m = 0 \rightarrow \frac { - 1 } { \sqrt { 15 } } \left( \begin{array}{lll} { 0 } & { 0 } & { 0 } \\{ 0 } & { 0 } & { 0 } \end{array} \right) } & { } \\{ m = 0 \rightarrow \frac { - 1 } { \sqrt { 15 } } \left( \begin{array}{lll} { 0 } & { 0 } & { \sqrt { 3 } } \\{ \sqrt { 3 } } & { 0 } & { 0 } \end{array} \right) } & { } \\{ \left( \begin{array}{lll} { 0 } & { 0 } & { 0 } \\{ 0 } & { 0 } & { \sqrt { 3 } } \end{array} \right) } & { } \\{ \left( \begin{array}{lll} { 0 } & { 0 } & { 0 } \\{ 0 } & { 0 } & { 0 } \end{array} \right) } & { } \\{ m = - 1 \rightarrow \frac { - 1 } { \sqrt { 15 } } \left( \begin{array}{lll} { 0 } & { 0 } & { 1 } \\{ 0 } & { - \sqrt { 3 } } & { 0 } \end{array} \right) } & { } \\{ \left( \begin{array}{lll} { 0 } & { 0 } & { 0 } \end{array} \right) } & { } \end{array}
$$

The following result is reached after taking steps parallel to those taken in Sec. D 1 for $d_{1m}^{l=2}$:

$$
\begin{array}{r} { \left[ \begin{array}{l} { c _ { 11 } ^{\omega} } \\{ c _ { 10 } ^{\omega} } \end{array} \right] = \underbrace { \frac { 1 } { \pi \sqrt { 6 } } \int d ^{3} \mathbf { r } \ \mathbf { J } _ { \omega } ( \mathbf { r } ) j _ { 0 } ( k r ) } _ { \tilde { l } = 0 } } \\{ - \underbrace { \frac { 1 } { \pi \sqrt { 6 } } \int d ^{3} \mathbf { r } \ \left\{ 3 \left[ \hat { \mathbf { r } } ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right] \hat { \mathbf { r } } - \mathbf { J } _ { \omega } ( \mathbf { r } ) \right\} j _ { 2 } ( k r ) } _ { \tilde { l } = 2 } . } \end{array}
$$