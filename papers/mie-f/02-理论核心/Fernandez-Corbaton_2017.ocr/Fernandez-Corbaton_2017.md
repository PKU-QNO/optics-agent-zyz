# SCIENTIFIC REPORTS

Received: 6 September 2016Accepted: 29 June 2017Published online: 08 August 2017

# On the dynamic toroidal multipoles from localized electric current distributions

Ivan Fernandez-Corbaton$^{1}$, Stefan Nanz$^{2}$ & Carsten Rockstuhl$^{1,2}$

We analyze the dynamic toroidal multipoles and prove that they do not have an independent physical meaning with respect to their interaction with electromagnetic waves. We analytically show how the split into electric and toroidal parts causes the appearance of non-radiative components in each of the two parts. These non-radiative components, which cancel each other when both parts are summed, preclude the separate determination of each part by means of measurements of the radiation from the source or of its coupling to external electromagnetic waves. In other words, there is no toroidal radiation or independent toroidal electromagnetic coupling. The formal meaning of the toroidal multipoles is clear in our derivations. They are the higher order terms of an expansion of the multipolar coefficients of electric parity with respect to the electromagnetic size of the source.

After the introduction of toroidal multipoles in the static case$^{1}$, the dynamic toroidal multipoles were presented as a new independent multipole family that had been previously ignored$^{2,3}$. The new family was derived from the split of the transverse multipoles of electric parity into two parts. These parts are often referred to as electric and toroidal. The dynamic toroidal multipoles have also been analyzed in refs 4 and 5, and are currently being considered in the areas of metamaterials, plasmonics, and nanophotonics$^{6-19}$.

In this article, we analyze the split between the dynamic electric and toroidal multipoles of a localized source distribution. We find that the two parts cannot be separately determined by measuring the electromagnetic fields produced by the source outside the source region. The two parts can also not be separately determined by measuring the coupling between the source and externally incident electromagnetic waves. The result applies to both near and far field situations, and implies that there is no independent coupling of toroidal character between the sources and the electromagnetic field, and that there is no radiation of pure toroidal character. The toroidal multipoles can hence not be considered an independent family. Rather, our analysis makes clear that the electric and toroidal parts correspond, respectively, to the lowest and the higher order terms of the expansion of the exact multipolar coefficients of electric parity with respect to the electromagnetic size of the source. In this respect, our article contains analytical expressions that inherently contain all correction orders: They are exact for any source size.

Our results do not question the usefulness of considering the higher order terms. For example, some experimental results can only be explained by adding the toroidal dipole contributions to the lowest order terms (see Fig. 3c in ref. 7, and Fig. 4 in ref. 16). The same is true for non-radiating spherical configurations (see Fig. 2 in ref. 20). These cases are examples where the toroidal terms are the dominant dipolar terms.

In the following, we first outline the mathematical setting in which we carry out the analysis. We then highlight the direct connections between our momentum space approach and the physics of multipolar couplings between sources and fields. On the one hand, three kinds of degrees of freedom are needed to describe the sources. Two of them are transverse and have opposite (electric vs. magnetic) parity, and the other one is longitudinal. On the other hand, only the two transverse degrees of freedom are needed to describe the electromagnetic fields produced by the sources outside the source region, where the field produced by the longitudinal degrees of freedom is identically zero.

Then, we analyze the physical meaning of the toroidal multipoles. Our analysis starts from recently obtained exact analytical expressions for the transverse multipolar coefficients of electric parity. These expressions are valid for any source size$^{21}$. We take the dipolar case as the guiding example, make the small source approximation keeping the two lowest orders, and show that: The lowest order term is the well known approximate expression

![](images/4c9fd64b59edb75d0adfa0d1676cf450ff7ec7cd1b4e63ea12158a25aaa69886_40.jpg){width=40%} Figure 1. The monochromatic electric current density distribution $\mathbf{J}_{\omega}(\mathbf{r})$ is confined to a sphere of radius $R$: The source region. In this article, we consider the electromagnetic fields produced by the source outside its region, i.e. $[\mathbf{E}_{\omega}(\mathbf{r}), \mathbf{H}_{\omega}(\mathbf{r})]$ for $|\mathbf{r}| > R$. These fields are completely determined by the Fourier components of the current density which meet $|\mathbf{p}| = \omega/c$ (see Fig. 2). The other components do not produce fields outside the source region. This is a general result that is also valid when the confining volume defining the source region is not spherical (see text).

for the electric dipole of electromagnetically small sources; the term of second lowest order is the approximate expression for the toroidal dipole of electromagnetically small sources [Eq. (2.11) in ref. 3]. We then analyze the original split$^{2,3}$ in the general multipolar case, and establish that both electric and toroidal parts contain non-radiative components, which appear due to the separation of terms of different order in the size of the source. These non-radiative components, which cancel each other when both parts are summed, preclude the separate determination of each part by measuring the radiation from the source outside the source region, or by measuring the coupling between the source and externally incident electromagnetic waves. Afterwards, we analyze a different class of splits where the two parts are free of this kind of non-radiative components. We find that, in this case, what precludes their independent measurement is the absence of longitudinal radiation. We show in Supp. Inf. Sec. IV that this is the same reason that precludes the independent measurement of the recently proposed re-definition of toroidal multipoles (Box 2 in ref. 19).

Finally, we use the obtained insights to clarify some statements that are often found in the literature

# Mathematical setting

We start with an electric $\bar{\text{current density distribution}}$ $\mathbf{J}(\mathbf{r}, t)$ embedded in an isotropic homogeneous medium characterized by real valued permittivity $\epsilon$ and permeability $\mu$. We assume that $\mathbf{J}(\mathbf{r}, t)$ is confined in space so that $\mathbf{J}(\mathbf{r}, t)=0$ for $|\mathbf{r}|>R$. We consider its energy-momentum Fourier representation

$$
\begin{array}{rl} { \mathbf { J } ( \mathbf { r } , \ t ) } & { = \ \mathcal { R } \Big [ \int _ { 0 ^{+} } ^{\infty} \frac { d \omega } { \sqrt { 2 \pi } } \exp ( - i \omega t ) \mathbf { J } _ { \omega } ( \mathbf { r } ) \Big ] , } \\& { = \ \mathcal { R } \Big [ \int _ { 0 ^{+} } ^{\infty} \frac { d \omega } { \sqrt { 2 \pi } } \exp ( - i \omega t ) \int \frac { d ^{3} \mathbf { p } } { \sqrt { ( 2 \pi ) ^{3} } } \mathbf { J } _ { \omega } ( \mathbf { p } ) \exp ( i \mathbf { p } \cdot \mathbf { r } ) \Big ] , } \end{array}
$$

and treat each frequency $\omega$ separately. The lower limit of the integral in $d\omega$ excludes the static case $\omega=0$, which we do not treat in this paper. This formal setting is independent of the cause of the current. For example, in a scattering situation the current is induced in the scatterer by an external field.

The $\bar{\epsilon}$ electromagnetic fields radiated by the source at each frequency $\omega$ are solely determined by the part of $\mathbf{J}_{\omega}(\mathbf{p})$ in the domain that satisfies $|\mathbf{p}|=\omega_{\sqrt{\epsilon\mu}}=\omega/c$. This theorem has been proven in refs 22 and 23. The authors showed that this part of the current completely determines the electromagnetic field generated by the source at any point $\mathbf{r}$ such that $|\mathbf{r}|>R$, which, in particular, includes near fields. This result has been extended beyond spheres to confining volumes of any smooth enough shape (see Chap. 9 in ref. 24): The part of $\mathbf{J}_{\omega}(\mathbf{p})$ in the domain that satisfies $|\mathbf{p}|=\omega_{\sqrt{\epsilon\mu}}=\omega/c$ determines the electromagnetic field generated by the source at any point outside the source region, for a wide class of shapes of such source region. Figure 1 depicts a spatially confined monochromatic source distribution and the fields that it generates outside the source region.

![](images/7727704b1696b8ce87847d42b463c55ca24d0d0cbc700dea90d8e4f38a214679_40.jpg){width=40%} Figure 2. Only the transverse components of the current density $\mathbf{J}_{\mathrm{a}}(\mathbf{p})$ with $\mathbf{p}=\frac{\omega}{c}$ $\hat{\mathbf{p}}$ produce electromagnetic fields outside the source region (see Fig. 1). (a1) Spherical shell of radius $|\mathbf{p}|=\frac{\omega}{c}$ in momentum space. The (a2) region depicts two different orthonormal bases for vector functions defined on the shell. The $\{\mathbf{X}_{jm}(\hat{\mathbf{p}}),\mathbf{Z}_{jm}(\hat{\mathbf{p}}),\mathbf{W}_{jm}(\hat{\mathbf{p}})\}$ and the $\{\mathbf{Y}_{j,j,m}(\hat{\mathbf{p}}),\mathbf{Y}_{j,j+1,m}(\hat{\mathbf{p}}),\mathbf{Y}_{j,j+1,m}(\hat{\mathbf{p}})\}$. The $(j,m)$ indexes are omitted in the figure, and the subscript in the $\mathbf{Y}$'s is the difference between their second and first indexes. The two bases are related to each other as written in Eq. (7). With respect to their polarization vectors: $\mathbf{X}_{jm}(\hat{\mathbf{p}}),\mathbf{Z}_{jm}(\hat{\mathbf{p}})$, and $\mathbf{Y}_{j,j,m}(\hat{\mathbf{p}})$ are orthogonal (transverse) to the momentum vector $\mathbf{p},\mathbf{W}_{jm}(\hat{\mathbf{p}})$ is parallel (longitudinal) to $\mathbf{p}$, and $\mathbf{Y}_{j,j+1,m}(\hat{\mathbf{p}})$ and $\mathbf{Y}_{j,j-1,m}(\hat{\mathbf{p}})$ lay in the $\mathbf{W}_{jm}(\hat{\mathbf{p}})-\mathbf{Z}_{jm}(\hat{\mathbf{p}})$ plane and are neither transverse nor longitudinal, as seen in (a3). The transverse vectors are represented by dashed blue arrows, the longitudinal ones by solid black arrows and the ones of mixed character by dotted red arrows. For the figure, we took $j=1$ in Eq. (7) for the relationships between $\{\mathbf{Z}(\hat{\mathbf{p}}),\mathbf{W}(\hat{\mathbf{p}})\}$ and $\{\mathbf{Y}_{-1}(\hat{\mathbf{p}}),\mathbf{Y}_{-1}(\hat{\mathbf{p}})\}$.

We denote by $\hat{\mathbf{J}}_{\omega}(\hat{\mathbf{p}})$ the components of $\mathbf{J}_{\omega}(\mathbf{p})$ in the spherical shell of radius $|\mathbf{p}|=\omega/c$ as a function of the solid angle $\hat{\mathbf{p}}=\mathbf{p}/|\mathbf{p}|$ [see region (a1) in Fig. 2].

In this domain, the relevant scalar product is $\langle A|B\rangle=\int d\hat{\mathbf{p}}\hat{A}^{\dagger}(\hat{\mathbf{p}})\mathbf{B}(\hat{\mathbf{p}})$, where $^{\dagger}$ denotes conjugate transpose, and $\hat{\mathbf{p}}$ runs over the entire spherical shell.

We expand $\mathbf{J}_{\omega}(\hat{\mathbf{p}})$ in an orthonormal basis for vector functions defined in a spherical shell:

$$
\mathring { \mathbf { J } } _ { \omega } ( \hat { \mathbf { p } } ) = \sum _ { j m } a _ { j m } ^{\omega} \mathbf { Z } _ { j m } ( \hat { \mathbf { p } } ) \ + \ b _ { j m } ^{\omega} \mathbf { X } _ { j m } ( \hat { \mathbf { p } } ) \ + \ c _ { j m } ^{\omega} \mathbf { W } _ { j m } ( \hat { \mathbf { p } } ) .
$$

The basis is composed by the three families of vector multipolar functions in momentum space (Sec. B$_r$3 in ref. 25)

$$
\begin{array}{rl} { \mathbf { X } _ { j m } ( \hat { \mathbf { p } } ) } & { = \frac { 1 } { \sqrt { j ( j + 1 ) } } \mathbf { L } Y _ { j m } ( \hat { \mathbf { p } } ) , } \\{ \mathbf { Z } _ { j m } ( \hat { \mathbf { p } } ) } & { = i \hat { \mathbf { p } } \times \mathbf { X } _ { j m } ( \hat { \mathbf { p } } ) , } \\{ \mathbf { W } _ { j m } ( \hat { \mathbf { p } } ) } & { = \hat { \mathbf { p } } Y _ { j m } ( \hat { \mathbf { p } } ) , } \end{array}
$$

where the $Y_{lm}(\hat{\mathbf{p}})$ are the scalar spherical harmonics and the three components of the vector $\mathbf{L}$ are the angular momentum operators for scalar functions.

Each of the functions in Eq. (3) is an eigenstate of the angular momentum squared $J^2$, the angular momentum along one axis $\hat{\alpha}$, for which we choose $\hat{\alpha} = \hat{\mathbf{z}}$, and the parity operator $\Pi$. As depicted in Fig. 2, the polarization of $\mathbf{X}_{jm}(\hat{\mathbf{p}})$ and $\mathbf{Z}_{jm}(\hat{\mathbf{p}})$ is orthogonal (transverse) to $\hat{\mathbf{p}}$, and the polarization of $\mathbf{W}_{jm}(\hat{\mathbf{p}})$ is parallel (longitudinal) to $\hat{\mathbf{p}}$ [see region (a2) in Fig. 2]. In coordinate space (r), this distinction corresponds to the distinction between divergence free (transverse) and curl free (longitudinal) vector fields. Table 1 contains the eigenvalues for the aforementioned three operators and the transverse ($\perp$) or longitudinal ($\parallel$) character of each vector multipolar function.

We provide expressions for the {$a_{jm}^{\omega}$, $b_{jm}^{\omega}$, $c_{jm}^{\omega}$} in Supp. Info. Sec. 1, which we derived in ref. 21.

|  | J ′ | J z | $Π$ | Polarization |
| --- | --- | --- | --- | --- |
| X jm ( j +1 ) | m | ( -1 ) + 1 | ± |
| Z jm ( j +1 ) | m | ( -1 ) + | ± |
| W jm ( j +1 ) | m | ( -1 ) + | $||$ |

Table 1. Vector multipolar functions: Polarization character and eigenvalues of $f^2$, $J_z$ and parity II. The symbol $\perp$ means transverse polarization. The symbol $\parallel$ means longitudinal polarization. Both $j$ and $m$ are integers, and $m = -j \ldots j$. For $\mathbf{X}_{jm}(\hat{\mathbf{p}})$ and $\mathbf{Z}_{jm}(\hat{\mathbf{p}})$, $j > 0$. For $\mathbf{W}_{jm}(\hat{\mathbf{p}})$, $j \geq 0$.

Multipolar coupling between sources and fields in momentum space. The decomposition in Eq. (2) is useful for discussing the physics of multipolar couplings between the sources and the fields. The complex scalars {$a_{jm}^{\omega}$, $b_{jm}^{\omega}$} determine the coupling of the source to the transverse electromagnetic field, a.k.a radiation field, a.k.a electromagnetic waves. The one-to-one relationship between the {$a_{jm}^{\omega}$, $b_{jm}^{\omega}$} coefficients of the source and the multipolar fields of frequency $\omega$ radiated by it is exposed in App. B of ref. 26, Chap. 9.10 in ref. 27, and ref. 23, for example, where the analysis is made in the $\mathbf{r}$ domain. The {$a_{jm}^{\omega}$, $b_{jm}^{\omega}$} represent independent degrees of freedom in the following sense. Each individual coefficient is connected to the radiation (absorption) of a particular kind of electromagnetic wave: A transverse multipolar field with well defined frequency, angular momentum, and parity. The $a_{jm}^{\omega}$ are connected to the multipolar waves of electric parity and the $b_{jm}^{\omega}$ to those of magnetic parity (see Table 1). The multipolar waves connected to different coefficients are orthogonal to each other. In principle, each individual {$a_{jm}^{\omega}$, $b_{jm}^{\omega}$} can be independently measured through the interaction of the source with the radiation field.

The $c_{jm}^{\omega}$ represent the longitudinal degrees of freedom of $\mathbf{J}_{\omega}(\hat{\mathbf{p}})$, but the longitudinal electric field with $|\mathbf{p}|=\omega/c$ is zero outside the source region defined in Fig. 1. This can be explained in the following way. The longitudinal components of the current ($c_{jm}^{\omega}$) generate a longitudinal electric field outside the source region defined in Fig. 1, but such field is canceled by the longitudinal electric field produced by the associated charge density. This statement follows from the continuity equation, as we show in Supp. Info. Sec. II. The cancellation can also be recognized in §13.3 p1875–1877 in ref. 28, and in the expression of the electric field in Eq. (2.39) in ref. 5, where the two contributions to the longitudinal field cancel exactly. In ref. 5 the longitudinal wave functions are $\mathcal{F}_{im\omega/c}^{(-)}(\mathbf{r})$.

The bottom line is that the {$a_{jm}^{\omega}$, $b_{jm}^{\omega}$} contain the necessary and sufficient information to determine both the fields of frequency $\omega$ produced by the sources outside the source region, and the coupling of the sources to external electromagnetic waves of such frequency.

The lack of longitudinal radiation means that, even though there are three kinds of degrees of freedom in the current, {$a_{jm}^{\omega}$, $b_{jm}^{\omega}$, $c_{jm}^{\omega}$}, only two of them are observable from outside the source region. The powerful theory developed by Gustav Mie for spherical scatterers$^{29}$ is probably the simplest example of this. In this case, the current density is induced in the sphere by an external incident field. The {$a_{jm}^{\omega}$, $b_{jm}^{\omega}$} of this induced current are determined by the Mie coefficients, which can be obtained analytically thanks to the symmetry of the problem. Using the Mie coefficients, the field produced by the induced current can be determined exactly everywhere outside the sphere. This allows the exact calculation of near fields, which is crucial in many applications like for example: Determination of the transition rates of atoms placed near spheres$^{30}$, determination of the forces and torques caused by evanescent fields onto a sphere near a substrate$^{31}$, modeling the tips of scanning tunnelling optical microscopes$^{32}$, and general optical trapping analysis$^{33}$.

# The dynamic toroidal multipoles

We will now study the split of the multipolar coefficients of electric parity ($a_{jm}^{\omega}$) which lead to the appearance of the dynamic toroidal multipoles$^{2,3}$. We use the dipolar case $j=1$ as our guiding example and then generalize the findings to any $j\geq1$.

We first show that the well known expressions for the electric and toroidal dipoles of small sources are, respectively, the lowest and second lowest order terms in a series expansion of the exact expression of $a_{1m}^{\omega}$.

Formal meaning. We start from the recently obtained exact expression for the dipolar vector of electric parity in the spherical vector basis $\mathbf{a}_{1}^{\omega}=[a_{11}^{\omega},a_{10}^{\omega},a_{1-1}^{\omega}]^{T}$ (Eq. (21) in ref. 21):

$$
\begin{array}{rl} { \mathbf { a } _ { 1 } ^{\omega} } & { = \ - \frac { 1 } { \pi \sqrt { 3 } } \int d ^{3} \mathbf { r } \mathbf { J } _ { \omega } ( \mathbf { r } ) j _ { 0 } ( k r ) } \\& {  - \frac { 1 } { 2 \pi \sqrt { 3 } } \int d ^{3} \mathbf { r } \Bigg \{ 3 [ \hat { \mathbf { r } } ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) ] \ \hat { \mathbf { r } } - \mathbf { J } _ { \omega } ( \mathbf { r } ) \Bigg \} , j _ { 2 } ( k r ) , } \end{array}
$$

where $k=\omega/c$, and $^\dagger$ means conjugate transpose. Let us now make the small argument approximation to the spherical Bessel functions with terms up to second order $[j_0(kr)\approx1-(kr)^2/6$ and $j_2(kr)\approx(kr)^2/15]$, and then group the contributions with the same power of $k$.

$$
\mathbf { a } _ { 1 } ^{\omega} \approx \underbrace { - \frac { 1 } { \pi \sqrt { 3 } } \int d ^{3} \mathbf { r } \mathbf { J } _ { \omega } ( \mathbf { r } ) } _ { \mathbf { e } _ { 1 } ^{\omega} }
$$

$$
- \frac { 1 } { \pi \sqrt { 3 } } k ^{2} \frac { \int d ^{3} \mathbf { r } \frac { 1 } { 10 } \left\{ [ \mathbf { r } ^{\dagger} \mathbf { J } _ { \omega } ( \mathbf { r } ) ] \mathbf { r } - 2 r ^{2} \mathbf { J } _ { \omega } ( \mathbf { r } ) \right\} } { \mathbf { t } ^{\dagger} } .
$$

We find that the $(k)^0$ term, $\mathbf{e}_1^\omega$ in Eq. (5), is the well known small source approximation of the electric dipole moment of a current density distribution [Eq. (9.14) in ref. 27]. The $k^2$ term, $\mathbf{t}_1^\omega$ in Eq. (6), is the small source approximation of the toroidal dipole moment [Eq. (2.11) in ref. 3]. The $\mathbf{t}_1^\omega$ integral in Eq. (6) contains contributions from the two integrals in Eq. (4): It is the sum of the terms of order $k^2$ coming from both $j_0(kr)$ in the first integral of Eq. (4) and $j_2(kr)$ in the second.

It is now clear that $\mathbf{t}_{1}^{\omega}$ is nothing but the next to leading order term in the electromagnetically small source approximation of the exact expression of $\mathbf{a}_{1}^{\omega}$. All higher order terms are easily obtained from the Taylor series of the spherical Bessel functions in Eq. (4).

The same structure revealed in Eqs (4)-(6) underlies the general case of the electric/toroidal split for $j \geq 1$. In refs 2 and 3, the lowest order term in $a_{jm}^{\omega}$ of order $(k)^{l-1}$, is isolated as in Eq. (5). The rest, $\mathbf{a}_{1}^{\omega} - \mathbf{e}_{1}^{\omega}$ in our example, is called toroidal multipole form factor. Then, the lowest order term of the toroidal multipole form factor, of order $(k)^{l+1}$ [like our Eq. (6)], is called toroidal multipole moment. For simplicity, we refer to the toroidal multipole form factor as the toroidal part. It corresponds to the toroidal multipolar family as defined in refs 2 and 3. In the dipolar example, the toroidal part ($\mathbf{a}_{1}^{\omega} - \mathbf{e}_{1}^{\omega}$) is equal to $-\frac{k^{2}}{\pi/\sqrt{3}}\mathbf{t}_{1}^{\omega}$ plus all other higher order corrections coming from the terms $(k)^{\omega>2}$ of the expansion of the spherical Bessel functions in Eq. (4).

The formal origin of the toroidal multipoles is recognized in the literature$^{4,15,18,20}$. We now investigate their physical meaning.

Physical meaning. The splitting of $\mathbf{a}_{m}^{\omega}$ into two parts$^{2,3}$ has a physically relevant consequence. Both parts, often called electric and toroidal, contain Fourier components of the current from outside the $|\mathbf{p}|=\omega/c$ shell. The $|\mathbf{p}|\neq\omega/c$ components do not couple to electromagnetic waves$^{23}$. For example, it follows from the properties of the Fourier transform that the result of the integral $\int d^{3}\mathbf{r}_{\mathbf{J}_{\omega}}(\mathbf{r})$ in the expression of the electric part in Eq. (5) is proportional to $\mathbf{J}_{\omega}(\mathbf{p}=0)$. Since $|\mathbf{p}|=0\neq\omega/c$, it follows that the toroidal part, $\mathbf{a}_{1}^{\omega}=\mathbf{e}_{1}^{\omega}$, must also contain a contribution proportional to $\mathbf{J}_{\omega}(\mathbf{p}=0)$. This is so because $\mathbf{a}_{1}^{\omega}$ does not have any out of shell contribution [Eq. (4.12a) in ref. [23]: The out of shell contributions in the electric part must be canceled by those in the toroidal part when the two parts are summed. Since the $|\mathbf{p}|\neq\omega/c$ components do not couple to the transverse electromagnetic field, it is impossible to determine the toroidal (electric) parts of $\mathbf{a}_{1}^{\omega}$ by measuring the fields produced by the source outside its region, or by externally exciting the source with electromagnetic waves. As previously discussed, this conclusion does not depend on whether the measurement(excitation) occurs in(from) the near, mid, or far field zones, as long as they occur outside the source region. For the sake of discussion, let us now consider the hypothetical case where the first term in the Taylor series of a given component of $\mathbf{a}_{1}^{\omega}$ is zero at a particular frequency. We make no judgment about whether this hypothesis is physically realizable. In this case, the toroidal part would be equal to the said component of $\mathbf{a}_{1}^{\omega}$ and, as such, it would couple to the transverse electromagnetic field. Nevertheless, in this hypothetical case the statement that the toroidal part couples to the field means nothing else than that $\mathbf{a}_{1}^{\omega}$ couples to the field, and it would not amount to separate coupling of the electric and toroidal parts.

The same conclusion applies to any value of $j \geq 1$, as we show in Supp. Inf. Sec. III. The root cause is the breaking up of the spherical Bessel functions in the split$^{2,3}$. Their lowest order term, proportional to $(kr)^{j-1}$, goes to the electric part and the rest of the terms go to the toroidal part. When unsplit, the spherical Bessel functions in exact integral expressions like Eq. (4) or Supp. Inf. Eq. (2) completely reject the $|\mathbf{p}| \neq \omega / c$ components of $\mathbf{J}_{\omega}(\mathbf{r})$. The Fourier transforms of spherical Bessel functions correspond to momentum space radial deltas $\delta(|\mathbf{p}| - \omega / c)$ (see end of Sec. III in ref. [21]). After the split, the term $(kr)^{j-1}$ by itself does not provide such rejection. This allows $|\mathbf{p}| \neq \omega / c$ components to "leak into" the electric part, and to be forcefully present in the toroidal part as well since the sum of the two parts does not contain any out of shell contribution.

We have hence established that the electric and toroidal parts cannot be separately determined by measuring the electromagnetic fields produced by the source outside its region, or by measuring its coupling to external electromagnetic waves. Our result implies that, as opposed to electric and magnetic multipoles whose distinct character is given by their parity, there is no electromagnetic field of pure toroidal character. It also implies that toroidal multipoles cannot be independently excited, i.e. there is no independent toroidal coupling. This precludes the existence of selection rules of toroidal character. The two different parities (electric and magnetic), and their linear combinations are necessary and sufficient to characterize electromagnetic transitions (see e.g. Chap. 9.8 p. 436 in ref. 27, and Chap. XII 2. B in ref. 26). The lack of longitudinal coupling together with the binary character of the parity operator leave no room for a third option.

While the $a_{jm}^{\omega}$ have an independent physical meaning, the individual electric and toroidal parts do not have it. The toroidal multipoles cannot be considered an independent family. The same can be said about the isolated electric part, or about any split of the terms in the Taylor series of the spherical Bessel functions in Supp. Info. Eq. (2) or (4). Any such split is bound to introduce non-radiative out of shell components in each of its parts.

Since the toroidal multipoles are higher order terms in the approximation of physically meaningful quantities, they can be used to improve analytical models that use only the lowest order terms. The inclusion of the next to leading order term improves the accuracy and prediction ability of such models, as can be seen in refs 7, 11, 12, 14–18. In ref. 20, and in the context of non-radiating source configurations, the inclusion of the second order term explains a zero in the induced $\mathbf{a}_{1}^{\omega}$, which cannot be explained by the first order term alone (see Fig. 2 in ref. 20). The improvement of the models will be maximized by using expressions like Eq. (4), Eq. (20) in ref. 21,

Table 2. Vector spherical harmonics: Polarization character and eigenvalues of $J^2$, $J_z$, $\Pi$, and $L^2$. $L^2$ is the orbital angular momentum squared. Both $j \geq 0$ and $m = -j \dots j$ are integers. For $j=0$, $\mathbf{Y}_{0,1,0} = -\hat{\mathbf{p}}/(4\pi)$, $\mathbf{Y}_{0,0,0} = 0$, and $\mathbf{Y}_{0,-1,0}$ is not defined.

|  | f 2 | J z | II | L 2 | Polarization |
| --- | --- | --- | --- | --- | --- |
| $Y j , j , m ( β )$ | j ( j + 1) | m | ( -1 ) j + 1 | j ( j + 1) | $⊥$ |
| $Y j , j , l - m ( β )$ | j ( j + 1) | m | ( -1 ) j | ( j + 1) | mixed |
| $Y j , j , l + m ( β )$ | j ( j + 1) | m | ( -1 ) j | ( j + 1) j + 2 | mixed |

and Supp. Inf. Eq. (2). These expressions inherently contain all correction orders because they are exact for any size of the source.

Splits without out of shell components. We have seen that the out of shell non-radiative components appear when splitting $a_{jm}^{\omega}$ by separating terms of different orders in the size of the source. Nevertheless, we observe that the $a_{jm}^{\omega}$ in Supp. Inf. Eq. (2) [$a_{jm}^{\omega}$ in Eq. (4)] have two formally distinct contributions, and that each of them contains a spherical Bessel function which guarantees the restriction to $|\mathbf{p}|=\omega/c$, thereby avoiding the intrusion of the out of shell components. However, we will now show that, due to the absence of longitudinal radiation, the two on-shell contributions cannot be separately determined. We consider another orthonormal basis for vector functions on the momentum shell: The vector spherical harmonics $\mathbf{Y}_{j,l,m}(\hat{\mathbf{p}})$. They are related to the $\{\mathbf{X}_{jm}(\hat{\mathbf{p}}),\mathbf{Z}_{jm}(\hat{\mathbf{p}}),\mathbf{W}_{jm}(\hat{\mathbf{p}})\}$ as

$$
\begin{array}{rl} { \mathbf { X } _ { j m } ( \hat { \mathbf { p } } ) } & { = \mathbf { Y } _ { j , j , m } ( \hat { \mathbf { p } } ) , } \\{ \mathbf { Z } _ { j m } ( \hat { \mathbf { p } } ) } & { = - \sqrt { \frac { j + 1 } { 2 j + 1 } } \mathbf { Y } _ { j , j - 1 , m } ( \hat { \mathbf { p } } ) - \sqrt { \frac { j } { 2 j + 1 } } \mathbf { Y } _ { j , j + 1 , m } ( \hat { \mathbf { p } } ) , } \\{ \mathbf { W } _ { j m } ( \hat { \mathbf { p } } ) } & { = \sqrt { \frac { j } { 2 j + 1 } } \mathbf { Y } _ { j , j - 1 , m } ( \hat { \mathbf { p } } ) - \sqrt { \frac { j + 1 } { 2 j + 1 } } \mathbf { Y } _ { j , j + 1 , m } ( \hat { \mathbf { p } } ) . } \end{array}
$$

The first and third lines of Eq. (7) can be found in Eq. (16.91) and Exercise 16.4.4 of ref. 34, respectively. The second line can be obtained from the equation $\mathbf{Z}_{jm}\sqrt{j(j+1)}=i\hat{\mathbf{p}}\times\mathbf{L}Y_{jm}$. The result is reached by using the expression of the orbital angular momentum operator in momentum space $\mathbf{L}=i\nabla_{\mathbf{p}}\times\mathbf{p}$, the formula $\mathbf{p}\times(\nabla_{\mathbf{p}}\times\mathbf{p})=\frac{\nabla|\mathbf{p}|^{2}}{\gamma}-(\mathbf{p}\cdot\nabla_{\mathbf{p}})\mathbf{p}$, and the gradient formula Eq. (16.94) in ref. 34.

Figure 2 illustrates Eq. (7). Table 2 contains information about the $\mathbf{Y}_{j,l,m}(\hat{\mathbf{p}})$. Notably, we deduce from Eq. (7) and see in Fig. 2 that, while $\mathbf{Y}_{j,j,m}(\hat{\mathbf{p}})$ is transverse, $\mathbf{Y}_{j,j-1,m}(\hat{\mathbf{p}})$ and $\mathbf{Y}_{j,j+1,m}(\hat{\mathbf{p}})$ are of mixed character, i.e., neither transverse nor longitudinal.

We can expand $J_{\omega}(\hat{\mathbf{p}})$ as:

$$
\mathbf { J } _ { \omega } ( \hat { \mathbf { p } } ) = \sum _ { j , m } \tau _ { j , j , m } ^{\omega} \mathbf { Y } _ { j , j , m } ( \hat { \mathbf { p } } ) \ + \ \tau _ { j , j - 1 , m } ^{\omega} \mathbf { Y } _ { j , j - 1 , m } ( \hat { \mathbf { p } } ) \ + \ \tau _ { j , j + 1 , m } ^{\omega} \mathbf { Y } _ { j , j + 1 , m } ( \hat { \mathbf { p } } ) .
$$

It follows from Eq. (7) that:

$$
\begin{array}{rl} { b _ { j m } ^{\omega} } & { = \tau _ { j , j , m } ^{\omega} , } \\{ a _ { j m } ^{\omega} } & { = - \sqrt { \frac { j + 1 } { 2 j + 1 } } \tau _ { j , j - 1 , m } ^{\omega} - \sqrt { \frac { j } { 2 j + 1 } } \tau _ { j , j + 1 , m } ^{\omega} , } \\{ c _ { j m } ^{\omega} } & { = \sqrt { \frac { j } { 2 j + 1 } } \tau _ { j , j - 1 , m } ^{\omega} - \sqrt { \frac { j + 1 } { 2 j + 1 } } \tau _ { j , j + 1 , m } ^{\omega} . } \end{array}
$$

We invert Eq. (9) to obtain:

$$
\begin{array}{rl} { \tau _ { j , j , m } ^{\omega} } & { = b _ { j m } ^{\omega} , } \\{ \tau _ { j , j - 1 , m } ^{\omega} } & { = - \sqrt { \frac { j + 1 } { 2 j + 1 } } a _ { j m } ^{\omega} + \sqrt { \frac { j } { 2 j + 1 } } c _ { j m } ^{\omega} , } \\{ \tau _ { j , j + 1 , m } ^{\omega} } & { = - \sqrt { \frac { j } { 2 j + 1 } } a _ { j m } ^{\omega} - \sqrt { \frac { j + 1 } { 2 j + 1 } } c _ { j m } ^{\omega} . } \end{array}
$$

The current dependent integrals in $\mathbf{r}$ space that define $\tau_{j,l,m}^{\omega}$ contain only the spherical Bessel function of order $l$. This can be shown using Eq. (10) and the expressions for $\{a_{jm}^{\omega}, b_{jm}^{\omega}, c_{jm}^{\omega}\}$ in Supp. Inf. Eq. (2). For example, in the dipole case of Eq. (4), the integrand that contains $j_{0}(kr)$ is only due to $\tau_{1,0,m}^{\omega}$, and the integrand that contains $j_{2}(kr)$ is only due to $\tau_{1,2,m}^{\omega}$. Both terms have zero out of shell components.

Let us assume that we want to determine $\tau_{j,j-1,m}^{\omega}$ and $\tau_{j,j+1,m}^{\omega}$ by measuring the electromagnetic radiation from the source at points $\mathbf{r}$ such that $|\mathbf{r}|>R$. As is clear from Eq. (10), and can be visually appreciated in Fig. 2, the

$\tau_{i,j\pm1,m}^{\omega}$ contain both transverse and longitudinal components. Their measurement involves the detection of both transverse and longitudinal fields generated by the current distribution. But, as previously discussed the longitudinal field due to the current distribution outside the source region is exactly canceled by that due to the charge distribution. Without access to the longitudinal degrees of freedom of $\hat{\mathbf{J}}_{\omega}(\hat{\mathbf{p}})$, it is impossible to separate the two $\tau_{i,l\pm1,m}^{\omega}$ contributions to $a_{lm}^{\omega}$.

We see that there are splits of $a_{jm}^{\omega}$ that, while both parts remain free of out of shell components, they contain longitudinal components which render them non-separable. This is the case for a definition of the toroidal multipoles that has been recently given in Box 2 of ref. [19]. In Supp. Info. Sec. [IV], we first show that this definition is different from the original definition in refs [2] and [3]. In the split of the $a_{jm}^{\omega}$ proposed in Box 2 of ref. [19], the integrands contain entire spherical Bessel functions which prevent the appearance of out of shell components. We then show that each of the two parts contains longitudinal components that cannot be detected from outside the source region.

# Discussion and conclusion

To finalize, we discuss some statements that are often found in the toroidal literature.

It is often stated that the toroidal multipole family is a third family, independent of the electric and magnetic ones$^{5,7,13,19}$. Originally, the authors of ref. 2 suggested in Sec. 4 to replace the $\{a_{jm}^{\omega}, b_{jm}^{\omega}, c_{jm}^{\omega}\}$ by $\{t_{jm}^{\omega}, b_{jm}^{\omega}, c_{jm}^{\omega}\}$, where $t_{jm}^{\omega}$ are the coefficients of the toroidal part of $a_{jm}^{\omega}$. We have shown that the $t_{jm}^{\omega}$ cannot be separately determined, and can hence not constitute a third independent multipolar family.

It is also often stated that three multipolar families, including the toroidal one, are needed in order to expand a general charge-current distribution, while the radiation that they emit can be described with only two multipolar families$^{5,14,35}$. Starting from Eq. (2), our analysis makes clear that, indeed, three multipolar families are needed to describe the source, and only two are needed to describe the fields radiated by it. It also makes clear that the third family is constituted by the longitudinal multipoles, and not the toroidal multipoles. The fact that the longitudinal field is zero outside the sources explains why the number of necessary multipolar families decreases by one when going from the sources to the fields.

Finally, it is also stated in refs 5 and 19 that the toroidal multipoles can be separated using spectroscopic techniques. The separation is to be enabled by exploiting the extra frequency dependent weighting of the toroidal multipoles [$k^{2}=(\omega/c)^{2}$] with respect to the electric multipoles. It is straightforward to prove that, should this be actually possible, there would exist a doubly infinite number of independent multipolar families, and not just a third one. This unphysical outcome shows that the conjectured separability is not possible. In order to show this, let us assume that it is possible. The steps going from Eqs (4)–(6) reveal that the extra $k^{2}$ scaling comes from different terms in the series expansion of the spherical Bessel functions. We stopped at the second lowest order, but each of the infinite number of terms in the complete expansion has an extra $k^{2}$ weight with respect to its predecessor. Additionally, one can make a similar expansion of the magnetic multipoles $b_{jm}^{i}$ (see Sec. 4 in ref. 21). If the separate measurement of the terms with additional $k^{2}$ factors where possible, as conjectured in Box 2 of ref. 19, there would be not just an extra independent multipolar family, but a doubly infinite number of them. The physical reality is that each of this doubly infinite number of formally obtained terms is not an independent degree of freedom. The multipolar electromagnetic transitions that determine the spectroscopic response of a system of charges and currents are completely characterized by using the two possible parities, electric and magnetic. The spectroscopic measurements of $\{a_{jm}^{\omega},b_{jm}^{j}\}$ already contain all the available information. On the other hand, should the analysis of the spectroscopic data make use of models limited to the lowest order, the inclusion of the second lowest order terms can only improve it, and the use of exact expressions like Eq. (4), Supp. Inf. Eq. (2), and Eq. (20) in ref. 21 will optimize it.

In conclusion: Our analysis proves that the dynamic toroidal multipoles do not have an independent physical meaning with respect to their interaction with electromagnetic waves. Their formal meaning is clear, however: They are higher order terms of an expansion of the transverse multipolar coefficients of electric parity in the electromagnetic size of the source.

# References

Zel'Dovich, I. B. Electromagnetic Interaction with Parity Violation. Sov. J. Exp. Theor. Phys. 6, 1184 (1958).

Dubovik, V. M. & Cheshkov, A. A. Multipole expansion in classical and quantum field theory and radiation. Sov. J. Part. Nucl. 5, 318-337 (1974).

Dubovik, V. M. & Tugushhev, V. V. Toroid moments in electrodynamics and solid-state physics. Phys. Rep. 187, 145-202 (1990).

Afaniev, G. N. Vector solutions of the laplace equation and the influence of helicity on aharonov-bohm scattering. J. Phys. A 27, 2143 (1994).

Radescu, E. & Vaman, G. Exact calculation of the angular momentum loss, recoil force, and radiation intensity for an arbitrary source in terms of electric, magnetic, and toroid multipoles. Phys. Rev. E 65, 046609 (2002).

Marinov, K., Boardman, A. D., Fedotov, V. A. & Zheludev, N. Toroidal metamaterial. New J. Phys. 9, 324 (2007).

Kaelberger, T., Fedotov, V. A., Papasimakis, N., Tsai, D. P. & Zheludev, N. I. Toroidal dipolar response in a metamaterial. Science 330, 1510-1512 (2010).

Dong, Z.-G., Ni, P., Zhu, J., Yin, X. & Zhang, X. Toroidal dipole response in a multifold double-ring metamaterial. Opt. Express 20, 13065-13070 (2012).

Dong, Z.-G., et al. Optical toroidal dipolar response by an asymmetric double-bar metamaterial. Appl. Phys. Lett. 101, 144105 (2012).

Ogut, B., Talebi, N., Vogelgesang, R., Sigle, W. & Van Aken, P. A. Toroidal plasmonic eigenmodes in oligomer nanocavities for the visible. Nano Lett. 12, 5239-5244 (2012).

Huang, Y.-W. et al. Design of plasmonic toroidal metamaterials at optical frequencies. Opt. Express 20, 1760-1768 (2012).

Fan, Y., Wei, Z., Li, H., Chen, H. & Soukoulis, C. M. Low-loss and high-$q$ planar metamaterial with toroidal moment. Phys. Rev. B 87, 115417 (2013).

Fedotov, V. A., Rogacheva, A., Savinov, V., Tsai, D. & Zheludev, N. I. Resonant transparency and non-trivial non-radiating excitations in toroidal metamaterials. Scientific reports 3, 2967 (2013).

Savinov, V., Fedotov, V. & Zheludev, N. Toroidal dipolar excitation and macroscopic electromagnetic properties of metamaterials. Phys. Rev. B 89, 205112 (2014).

Liu, W. Zhang, J., Lei, B. & Hu, H. Toroidal dipole induced transparency for core-shell nanoparticles. arXiv preprint arXiv:1412.4931 (2014).

Basharin, A. A. et al. Dielectric metamaterials with toroidal dipolar response. Phys. Rev. X 5, 011036 (2015).

Liu, W. Zhang, J., Lei, B., Hu, H. & Miroshnichenko, A. E. Invisible excitation and tuning of toroidal dipoles within individual homogenous nanoparticles. arXiv preprint arXiv:1508.02520 (2015).

Liu, W., Shi, J., Lei, B., Hu, H. & Miroshnichenko, A. E. Efficient excitation and tuning of toroidal dipoles within individual homogenous nanoparticles. arXiv preprint arXiv:1508.02520 (2015).

Papasmakis, N., Fedotov, V. A., Savinov, V., Raybould, T. A. & Zheludev, N. I. Electromagnetic toroidal excitations in matter and free space. Nat. Mater. 15, 263–271 (2016).

Miroshnichenko, A. E. et al. Seeing the unseen: observation of an anapole with dielectric nanoparticles. arXiv preprint arXiv:1412.0299 (2014).

Fernandez-Corbaton, I., Nanz, S. Alae, R. & Rockstuhl, C. Exact dipolar moments of a localized electric current distribution. Opt. Express 23, 33044–33064 (2015).

Devaney, A. & Wolf, E. Radiating and nonradiating classical current distributions and the fields they generate. Physical Review D 8, 1044 (1973).

Devaney, A. J. & Wolf, E. Multipole expansions and plane wave representations of the electromagnetic field. J. Math. Phys. 15, 234–244 (1974).

Colton, D. & Kress, R. Inverse acoustic and electromagnetic scattering theory, vol. 93 (Springer Science & Business Media, New York, 2012).

Cohen-Tannoudji, C., Dupont-Roc, J. & Grynberg, G. Photons and Atoms: Introduction to Quantum Electrodynamics (Wiley, 1989) (Trans. of: Photons and atoms. InterEditions 1987).

Blatt, J. M. & Weisskopf, V. F. Theoretical Nuclear Physics (John Wiley & Sons Inc, 1952).

Jackson, J. D. Classical Electrodynamics (Wiley, 1998).

Morse, P. M. & Feshbach, H. Methods of Theoretical Physics (McGraw-Hill and Kogakusha Book Companies, 1953).

Mie, G. Beiträge zur Optik trüber Medien, speziell kolloidal Metallösungen. Annalen der Physik 330, 377–445 (1908).

Chew. H. Transition rates of atoms near spherical surfaces. J. Chem. Phys. 87, 1355–1360 (1987).

Chang, S. & Lee, S. S. Optical torque exerted on a sphere in the evanescent field of a circularly-polarized gaussian laser beam. Opt. Commun. 151, 286–296 (1998).

Barchiesi, D. & Van Labeke, D. Application of mie scattering of evanescent waves to scanning tunnelling optical microscopy theory. J. Mod. Opt. 40, 1239–1254 (1993).

Dienerowitz, M., Mazilu, M. & Dholakia, K. Optical manipulation of nanoparticles: a review. J. Nanophotonics. 2, 021875–021875 (2008).

Arfken, G. B., Weber, H.-J. & Harris, F. E. Mathematical Methods for Physicists: A Comprehensive Guide (Academic Press, 2012).

Zhang, X.-L., Wang, S., Lin, Z., Sun, H.-B. & Chan, C. Optical force on toroidal nanostructures: toroidal dipole versus renormalized electric dipole. Phys. Rev. A 92, 043804 (2015).

# Acknowledgements

We warmly thank Dr. Rasoul Alae for numerous discussions and for his feedback on the manuscript. We also warmly thank Dr. Mário Silveirinha for pointing out that our analysis and results are valid independently of the shape of the volume confining the sources. I.F.-C. thanks Ms. Magda Felo for her help with the figures. The work was partially supported by the DFG within the SFB project 1173. S.N. also acknowledges support by the Karlsruhe School of Optics & Photonics (KSOP). We acknowledge support by Deutsche Forschungsgemeinschaft and Open Access Publishing Fund of Karlsruhe Institute of Technology.

# Author Contributions

I.F.-C. did the analytical work that led to the results presented in the manuscript supported by S.N. C.R. initiated and supervised the research. All authors discussed the results and contributed to the manuscript.

# Additional Information

Supplementary information accompanies this paper at doi:10.1038/s41598-017-07474-

Competing Interests: The authors declare that they have no competing interests.

Publisher's note: Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

Open Access This article is licensed under a Creative Commons Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or

format, as long as you give appropriate credit to the original author(s) and the source, provide a link to the Creative Commons license, and indicate if changes were made. The images or other third party material in this article are included in the article's Creative Commons license, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons license and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/.

© The Author(s) 2017