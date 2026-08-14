import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * Alaee 2018 Fig. 3: scan-capable 3-D frequency-domain scattering builder.
 *
 * This is deliberately a batch-safe deterministic builder.  It uses the
 * Johnson-Christy Au nk table at the native tabulated points (520.9--1937 nm)
 * and linearly interpolates n and k at lambda0.  The default point is
 * x_alaee=0.5 (lambda0=1000 nm), inside the frozen JC support.  The host and
 * spacer are air pending the Fig. 3 human input gate; that choice is surfaced
 * in the stdout receipt and B17 report rather than silently promoted.
 *
 * The incident plane wave is configured through the EWFD interface's
 * BackgroundField property group in scattered-field formulation.  A PML is
 * optional; if the COMSOL 6.3 runtime rejects the geometry PML feature, the
 * exterior scattering boundary remains the configured open-boundary path and
 * the receipt says so.
 */
public class Alaee2018Fig3ComsolScattering {
  private static final double[] SPECTRUM_X = new double[] {
    0.26, 0.28, 0.30, 0.32, 0.34, 0.36, 0.38, 0.40, 0.42,
    0.44, 0.46, 0.48, 0.50, 0.54, 0.58, 0.62, 0.66, 0.70,
    0.74, 0.78, 0.82, 0.86, 0.90, 0.925, 0.95
  };
  private static String currentCaseId = "scan_x0500";
  private static double currentX = 0.5;
  private static double currentMeshScale = 1.0;
  private static double currentLboxNm = 3000.0;
  private static boolean currentExportFields = true;
  // Submission staging replaces exactly this fail-closed scheduling constant
  // in an immutable per-shard copy; the physical model below is unchanged.
  private static final String B30_SHARD = "invalid";

  private static final String[][] JC_NK = new String[][] {
    {"520.9", "0.62", "2.081"}, {"548.6", "0.43", "2.455"},
    {"582.1", "0.29", "2.863"}, {"616.8", "0.21", "3.272"},
    {"659.5", "0.14", "3.697"}, {"704.5", "0.13", "4.103"},
    {"756.0", "0.14", "4.542"}, {"821.1", "0.16", "5.083"},
    {"892.0", "0.17", "5.663"}, {"984.0", "0.22", "6.350"},
    {"1088.0", "0.27", "7.150"}, {"1216.0", "0.35", "8.145"},
    {"1393.0", "0.43", "9.519"}, {"1610.0", "0.56", "11.21"},
    {"1937.0", "0.92", "13.78"}
  };

  public static Model run() throws Exception {
    String shard = B30_SHARD;
    System.out.println(
      "ALAEE2018_FIG3_SCAN_BEGIN"
      + " shard=" + shard
      + " supported_x_min=0.26 supported_x_max=0.95"
      + " spectrum_points=" + SPECTRUM_X.length
      + " convergence_points=6"
      + " JC_support_nm=520.9:1937.0"
    );

    Model last;
    if (shard.equals("s2")) {
      last = runSpectrumRange(9, 15);
    } else if (shard.equals("s3")) {
      last = runSpectrumRange(15, 21);
    } else if (shard.equals("s4")) {
      last = runSpectrumRange(21, 25);
    } else if (shard.equals("conv_x500")) {
      last = runConvergencePoint(0.5);
    } else if (shard.equals("conv_x900")) {
      last = runConvergencePoint(0.9);
    } else if (shard.equals("b32_base_x360")) {
      last = runCase("b32_base_x360", 0.36, 1.0, 3000.0, false);
    } else if (shard.equals("b32_mesh070_x360")) {
      last = runCase("b32_mesh070_x360", 0.36, 0.7, 3000.0, false);
    } else if (shard.equals("b32_mesh050_x360")) {
      last = runCase("b32_mesh050_x360", 0.36, 0.5, 3000.0, false);
    } else if (shard.equals("b32_mesh030_x360")) {
      last = runCase("b32_mesh030_x360", 0.36, 0.3, 3000.0, false);
    } else if (shard.equals("b32_domain4000_x360")) {
      last = runCase("b32_domain4000_x360", 0.36, 1.0, 4000.0, false);
    } else {
      throw new IllegalArgumentException("Unsupported B30 shard: " + shard);
    }

    System.out.println(
      "ALAEE2018_FIG3_SCAN_END"
      + " shard=" + shard
      + " spectrum_points=" + SPECTRUM_X.length
      + " convergence_points=6"
      + " returned_case=" + currentCaseId
    );
    return last;
  }

  private static Model runSpectrumRange(int firstInclusive, int lastExclusive) throws Exception {
    Model last = null;
    for (int i = firstInclusive; i < lastExclusive; i++) {
      double x = SPECTRUM_X[i];
      String suffix = Integer.toString((int)Math.round(1000.0*x));
      last = runCase("scan_x" + suffix, x, 1.0, 3000.0, Math.abs(x-0.5) < 1e-12);
      if (i + 1 < lastExclusive) ModelUtil.remove("Alaee2018Fig3");
    }
    return last;
  }

  private static Model runConvergencePoint(double x) throws Exception {
    String suffix = Integer.toString((int)Math.round(1000.0*x));
    Model coarse = runCase("mesh_coarse_x" + suffix, x, 1.3, 3000.0, false);
    ModelUtil.remove("Alaee2018Fig3");
    Model fine = runCase("mesh_fine_x" + suffix, x, 0.7, 3000.0, false);
    ModelUtil.remove("Alaee2018Fig3");
    return runCase("domain_4000_x" + suffix, x, 1.0, 4000.0, false);
  }

  private static Model runCase(
      String caseId,
      double xAlaee,
      double meshScale,
      double lboxNm,
      boolean exportFields) throws Exception {
    currentCaseId = caseId;
    currentX = xAlaee;
    currentMeshScale = meshScale;
    currentLboxNm = lboxNm;
    currentExportFields = exportFields;
    Model model = ModelUtil.create("Alaee2018Fig3");
    model.modelNode().create("comp1");
    setParameters(model);
    defineJohnsonChristy(model);
    buildGeometry(model);
    buildMaterials(model);
    boolean background = createBackgroundField(model);
    boolean sbc = createScatteringBoundary(model);
    boolean pml = tryCreatePml(model);
    buildMesh(model);
    applyMeshVariant(model);
    buildStudyAndSolve(model);
    boolean post = buildPostProcessing(model);

    int ne = model.mesh("mesh1").getNumElem();
    System.out.println(
      "ALAEE2018_FIG3_COMSOL_SCATTERING_OK"
      + " case_id=" + currentCaseId
      + " x_alaee=" + currentX
      + " lambda_nm=" + (500.0/currentX)
      + " mesh_scale=" + currentMeshScale
      + " Lbox_nm=" + currentLboxNm
      + " mesh_elements=" + ne
      + " background_field=" + background
      + " scattering_boundary=" + sbc
      + " pml=" + pml
      + " postprocessing_nodes=" + post
    );
    System.out.println(
      "ALAEE2018_FIG3_SCIENCE_STATUS"
      + " case_id=" + currentCaseId
      + " result_class=scan_point_configured_frequency_domain_candidate"
      + " host=air spacer=air"
      + " channels=ED,MD,EQ,MQ"
      + " JC_support_nm=520.9:1937.0"
      + " field_export=EHJ_Data_feature"
    );
    return model;
  }

  private static void setParameters(Model model) {
    model.param().set("a", "250[nm]");
    model.param().set("t", "80[nm]");
    model.param().set("g", "120[nm]");
    model.param().set("x_alaee", Double.toString(currentX));
    model.param().set("lambda0", "2*a/x_alaee");
    model.param().set("lambda_nm", "lambda0/1[nm]");
    model.param().set("freq0", "c_const/lambda0");
    model.param().set("k0", "2*pi/lambda0");
    model.param().set("E0", "1[V/m]");
    model.param().set("Lbox", Double.toString(currentLboxNm) + "[nm]");
    model.param().set("mesh_scale", Double.toString(currentMeshScale));
    model.param().set("host_n", "1");
    model.param().set("epsHost", "host_n^2");
  }

  private static void defineJohnsonChristy(Model model) {
    model.func().create("nAu", "Interpolation");
    model.func("nAu").set("funcname", "nAu");
    model.func("nAu").set("table", toTable(JC_NK, 1));
    model.func("nAu").set("interp", "linear");
    model.func("nAu").set("extrap", "none");
    model.func("nAu").set("argunit", "nm");
    model.func("nAu").set("fununit", "1");

    model.func().create("kAu", "Interpolation");
    model.func("kAu").set("funcname", "kAu");
    model.func("kAu").set("table", toTable(JC_NK, 2));
    model.func("kAu").set("interp", "linear");
    model.func("kAu").set("extrap", "none");
    model.func("kAu").set("argunit", "nm");
    model.func("kAu").set("fununit", "1");
  }

  private static String[][] toTable(String[][] src, int valueColumn) {
    String[][] out = new String[src.length][2];
    for (int i = 0; i < src.length; i++) {
      out[i][0] = src[i][0];
      out[i][1] = src[i][valueColumn];
    }
    return out;
  }

  private static void buildGeometry(Model model) {
    model.geom().create("geom1", 3);
    model.geom("geom1").lengthUnit("nm");
    model.geom("geom1").create("box", "Block");
    model.geom("geom1").feature("box").set("size", new String[]{"Lbox", "Lbox", "Lbox"});
    model.geom("geom1").feature("box").set("pos", new String[]{"-Lbox/2", "-Lbox/2", "-Lbox/2"});
    model.geom("geom1").feature("box").set("selresult", true);
    model.geom("geom1").feature("box").set("selresultshow", "bnd");

    model.geom("geom1").create("diskLower", "Cylinder");
    model.geom("geom1").feature("diskLower").set("r", "a");
    model.geom("geom1").feature("diskLower").set("h", "t");
    model.geom("geom1").feature("diskLower").set("pos", new String[]{"0", "0", "-g/2-t"});
    model.geom("geom1").feature("diskLower").set("selresult", true);
    model.geom("geom1").feature("diskLower").set("selresultshow", "dom");

    model.geom("geom1").create("diskUpper", "Cylinder");
    model.geom("geom1").feature("diskUpper").set("r", "a");
    model.geom("geom1").feature("diskUpper").set("h", "t");
    model.geom("geom1").feature("diskUpper").set("pos", new String[]{"0", "0", "g/2"});
    model.geom("geom1").feature("diskUpper").set("selresult", true);
    model.geom("geom1").feature("diskUpper").set("selresultshow", "dom");
    model.geom("geom1").run();
  }

  private static void buildMaterials(Model model) {
    model.material().create("matHost", "Common");
    model.material("matHost").selection().all();
    model.material("matHost").propertyGroup("def").set("relpermittivity", new String[]{
      "epsHost", "0", "0", "0", "epsHost", "0", "0", "0", "epsHost"
    });
    model.material("matHost").propertyGroup("def").set("relpermeability", new String[]{
      "1", "0", "0", "0", "1", "0", "0", "0", "1"
    });

    model.material().create("matGoldLower", "Common");
    model.material("matGoldLower").selection().named("geom1_diskLower_dom");
    model.material("matGoldLower").propertyGroup("def").set("relpermittivity", new String[]{
      "epsAu", "0", "0", "0", "epsAu", "0", "0", "0", "epsAu"
    });
    model.material("matGoldLower").propertyGroup("def").set("relpermeability", new String[]{
      "1", "0", "0", "0", "1", "0", "0", "0", "1"
    });

    model.material().create("matGoldUpper", "Common");
    model.material("matGoldUpper").selection().named("geom1_diskUpper_dom");
    model.material("matGoldUpper").propertyGroup("def").set("relpermittivity", new String[]{
      "epsAu", "0", "0", "0", "epsAu", "0", "0", "0", "epsAu"
    });
    model.material("matGoldUpper").propertyGroup("def").set("relpermeability", new String[]{
      "1", "0", "0", "0", "1", "0", "0", "0", "1"
    });

    model.variable().create("matvars");
    // nAu/kAu declare argunit=nm, so pass the dimensional wavelength. COMSOL
    // then converts lambda0 to nm exactly once (1000 nm at x_alaee=0.5).
    model.variable("matvars").set("epsAu", "(nAu(lambda0)+i*kAu(lambda0))^2");
  }

  private static boolean createBackgroundField(Model model) {
    try {
      model.physics().create("ewfd", "ElectromagneticWavesFrequencyDomain", "geom1");
      model.physics("ewfd").prop("BackgroundField").set("SolveFor", "scatteredField");
      model.physics("ewfd").prop("BackgroundField").set("Eb", new String[]{
        "E0*exp(-i*k0*z)", "0", "0"
      });
      System.out.println(
        "ALAEE2018_FIG3_BACKGROUND_FIELD_OK"
        + " property_group=BackgroundField"
        + " solve_for=scatteredField"
        + " wave=user_defined_plane_wave"
        + " polarization=x propagation=+z"
        + " amplitude_V_per_m=1 phase=exp(-i*k0*z)"
      );
      return true;
    } catch (Throwable failure) {
      System.out.println(
        "ALAEE2018_FIG3_BACKGROUND_FIELD_ERROR"
        + " type=" + failure.getClass().getName()
        + " message=" + sanitizeMessage(failure.getMessage())
      );
      return false;
    }
  }

  private static boolean createScatteringBoundary(Model model) {
    String[] candidates = new String[]{"ScatteringBoundaryCondition", "Scattering"};
    for (int i = 0; i < candidates.length; i++) {
      try {
        model.physics("ewfd").create("sctr1", candidates[i], 2);
        try {
          model.physics("ewfd").feature("sctr1").selection().named("geom1_box_bnd");
        } catch (Throwable ignored) {
          model.physics("ewfd").feature("sctr1").selection().all();
        }
        return true;
      } catch (Throwable ignored) {
        try { model.physics("ewfd").feature().remove("sctr1"); } catch (Throwable ignored2) {}
      }
    }
    return false;
  }

  private static boolean tryCreatePml(Model model) {
    // The geometry PML feature is intentionally best-effort.  COMSOL 6.3
    // exports differ in the property key used to mark PML domains; SBC is the
    // deterministic fallback when this feature is unavailable.
    try {
      model.geom("geom1").feature().create("pml1", "PML");
      model.geom("geom1").feature("pml1").set("selresult", true);
      model.geom("geom1").run();
      return true;
    } catch (Throwable ignored) {
      try { model.geom("geom1").feature().remove("pml1"); } catch (Throwable ignored2) {}
      return false;
    }
  }

  private static void buildMesh(Model model) {
    model.mesh().create("mesh1", "geom1");
    // Adding explicit Size and FreeTet features switches the new mesh sequence
    // to user-controlled mode in COMSOL 6.3 without invoking the failing
    // physics-controlled-to-user-controlled conversion in automatic(false).
    model.mesh("mesh1").feature().create("size1", "Size");
    model.mesh("mesh1").feature("size1").set("hmax", "120[nm]");
    model.mesh("mesh1").feature("size1").set("hmin", "12[nm]");
    model.mesh("mesh1").feature().create("sizeGoldLower", "Size");
    model.mesh("mesh1").feature("sizeGoldLower").selection().named("geom1_diskLower_dom");
    model.mesh("mesh1").feature("sizeGoldLower").set("hmax", "35[nm]");
    model.mesh("mesh1").feature("sizeGoldLower").set("hmin", "8[nm]");
    model.mesh("mesh1").feature().create("sizeGoldUpper", "Size");
    model.mesh("mesh1").feature("sizeGoldUpper").selection().named("geom1_diskUpper_dom");
    model.mesh("mesh1").feature("sizeGoldUpper").set("hmax", "35[nm]");
    model.mesh("mesh1").feature("sizeGoldUpper").set("hmin", "8[nm]");
    model.mesh("mesh1").feature().create("ftet1", "FreeTet");
    model.mesh("mesh1").run();
    System.out.println(
      "ALAEE2018_FIG3_MESH_OK"
      + " case_id=" + currentCaseId
      + " mesh_scale=" + currentMeshScale
      + " Lbox_nm=" + currentLboxNm
      + " mesh_elements=" + model.mesh("mesh1").getNumElem()
      + " min_quality=" + model.mesh("mesh1").getMinQuality()
    );
  }

  private static void applyMeshVariant(Model model) {
    if (Math.abs(currentMeshScale-1.0) < 1e-12) return;
    model.mesh("mesh1").feature("size1").set(
      "hmax", Double.toString(120.0*currentMeshScale) + "[nm]"
    );
    model.mesh("mesh1").feature("size1").set(
      "hmin", Double.toString(12.0*currentMeshScale) + "[nm]"
    );
    model.mesh("mesh1").feature("sizeGoldLower").set(
      "hmax", Double.toString(35.0*currentMeshScale) + "[nm]"
    );
    model.mesh("mesh1").feature("sizeGoldLower").set(
      "hmin", Double.toString(8.0*currentMeshScale) + "[nm]"
    );
    model.mesh("mesh1").feature("sizeGoldUpper").set(
      "hmax", Double.toString(35.0*currentMeshScale) + "[nm]"
    );
    model.mesh("mesh1").feature("sizeGoldUpper").set(
      "hmin", Double.toString(8.0*currentMeshScale) + "[nm]"
    );
    model.mesh("mesh1").run();
    System.out.println(
      "ALAEE2018_FIG3_MESH_VARIANT_OK"
      + " case_id=" + currentCaseId
      + " mesh_scale=" + currentMeshScale
      + " mesh_elements=" + model.mesh("mesh1").getNumElem()
      + " min_quality=" + model.mesh("mesh1").getMinQuality()
    );
  }

  private static void buildStudyAndSolve(Model model) {
    model.study().create("std1");
    model.study("std1").create("freq", "Frequency");
    model.study("std1").feature("freq").set("plist", "freq0");
    model.sol().create("sol1");
    model.sol("sol1").study("std1");
    model.sol("sol1").createAutoSequence("std1");
    model.sol("sol1").runAll();
  }

  private static boolean buildPostProcessing(Model model) {
    String stage = "coupling_operators";
    try {
      model.cpl().create("intAuL", "Integration", "geom1");
      model.cpl("intAuL").selection().named("geom1_diskLower_dom");
      model.cpl("intAuL").set("opname", "intAuL");
      model.cpl().create("intAuU", "Integration", "geom1");
      model.cpl("intAuU").selection().named("geom1_diskUpper_dom");
      model.cpl("intAuU").set("opname", "intAuU");
      model.cpl().create("intBox", "Integration", "geom1");
      model.cpl("intBox").selection().named("geom1_box_bnd");
      model.cpl("intBox").set("opname", "intBox");

      stage = "multipole_variables";
      model.variable().create("post");
      model.variable("post").model("comp1");
      model.variable("post").set("omega0", "2*pi*freq0");
      model.variable("post").set("Jx", "-i*omega0*epsilon0_const*(epsAu-epsHost)*ewfd.Ex");
      model.variable("post").set("Jy", "-i*omega0*epsilon0_const*(epsAu-epsHost)*ewfd.Ey");
      model.variable("post").set("Jz", "-i*omega0*epsilon0_const*(epsAu-epsHost)*ewfd.Ez");
      model.variable("post").set("r2pp", "x^2+y^2+z^2");
      model.variable("post").set("rpp", "sqrt(r2pp)");
      model.variable("post").set("rhopp", "k0*rpp");
      model.variable("post").set("j0pp", "sin(rhopp)/rhopp");
      model.variable("post").set("j1orpp", "(sin(rhopp)-rhopp*cos(rhopp))/rhopp^3");
      model.variable("post").set("j2or2pp", "((3-rhopp^2)*sin(rhopp)-3*rhopp*cos(rhopp))/rhopp^5");
      model.variable("post").set("j3or3pp", "((15-6*rhopp^2)*sin(rhopp)-(15*rhopp-rhopp^3)*cos(rhopp))/rhopp^7");
      model.variable("post").set("rdotJpp", "x*Jx+y*Jy+z*Jz");
      model.variable("post").set("rcxJxpp", "y*Jz-z*Jy");
      model.variable("post").set("rcxJypp", "z*Jx-x*Jz");
      model.variable("post").set("rcxJzpp", "x*Jy-y*Jx");

      // Alaee Table 2 exact Cartesian moments.  The two disks stay at least
      // 60 nm from the origin, so rho never reaches the removable rho=0
      // singularities in these explicit spherical-Bessel quotients.
      model.variable("post").set("px", "i/omega0*(intAuL(Jx*j0pp+k0^2/2*(3*rdotJpp*x-r2pp*Jx)*j2or2pp)+intAuU(Jx*j0pp+k0^2/2*(3*rdotJpp*x-r2pp*Jx)*j2or2pp))");
      model.variable("post").set("py", "i/omega0*(intAuL(Jy*j0pp+k0^2/2*(3*rdotJpp*y-r2pp*Jy)*j2or2pp)+intAuU(Jy*j0pp+k0^2/2*(3*rdotJpp*y-r2pp*Jy)*j2or2pp))");
      model.variable("post").set("pz", "i/omega0*(intAuL(Jz*j0pp+k0^2/2*(3*rdotJpp*z-r2pp*Jz)*j2or2pp)+intAuU(Jz*j0pp+k0^2/2*(3*rdotJpp*z-r2pp*Jz)*j2or2pp))");
      model.variable("post").set("mx", "1.5*(intAuL(rcxJxpp*j1orpp)+intAuU(rcxJxpp*j1orpp))");
      model.variable("post").set("my", "1.5*(intAuL(rcxJypp*j1orpp)+intAuU(rcxJypp*j1orpp))");
      model.variable("post").set("mz", "1.5*(intAuL(rcxJzpp*j1orpp)+intAuU(rcxJzpp*j1orpp))");

      model.variable("post").set("qexx", "3*i/omega0*(intAuL((6*x*Jx-2*rdotJpp)*j1orpp+2*k0^2*(5*x^2*rdotJpp-2*x*Jx*r2pp-r2pp*rdotJpp)*j3or3pp)+intAuU((6*x*Jx-2*rdotJpp)*j1orpp+2*k0^2*(5*x^2*rdotJpp-2*x*Jx*r2pp-r2pp*rdotJpp)*j3or3pp))");
      model.variable("post").set("qeyy", "3*i/omega0*(intAuL((6*y*Jy-2*rdotJpp)*j1orpp+2*k0^2*(5*y^2*rdotJpp-2*y*Jy*r2pp-r2pp*rdotJpp)*j3or3pp)+intAuU((6*y*Jy-2*rdotJpp)*j1orpp+2*k0^2*(5*y^2*rdotJpp-2*y*Jy*r2pp-r2pp*rdotJpp)*j3or3pp))");
      model.variable("post").set("qezz", "3*i/omega0*(intAuL((6*z*Jz-2*rdotJpp)*j1orpp+2*k0^2*(5*z^2*rdotJpp-2*z*Jz*r2pp-r2pp*rdotJpp)*j3or3pp)+intAuU((6*z*Jz-2*rdotJpp)*j1orpp+2*k0^2*(5*z^2*rdotJpp-2*z*Jz*r2pp-r2pp*rdotJpp)*j3or3pp))");
      model.variable("post").set("qexy", "3*i/omega0*(intAuL(3*(y*Jx+x*Jy)*j1orpp+2*k0^2*(5*x*y*rdotJpp-(x*Jy+y*Jx)*r2pp)*j3or3pp)+intAuU(3*(y*Jx+x*Jy)*j1orpp+2*k0^2*(5*x*y*rdotJpp-(x*Jy+y*Jx)*r2pp)*j3or3pp))");
      model.variable("post").set("qexz", "3*i/omega0*(intAuL(3*(z*Jx+x*Jz)*j1orpp+2*k0^2*(5*x*z*rdotJpp-(x*Jz+z*Jx)*r2pp)*j3or3pp)+intAuU(3*(z*Jx+x*Jz)*j1orpp+2*k0^2*(5*x*z*rdotJpp-(x*Jz+z*Jx)*r2pp)*j3or3pp))");
      model.variable("post").set("qeyz", "3*i/omega0*(intAuL(3*(z*Jy+y*Jz)*j1orpp+2*k0^2*(5*y*z*rdotJpp-(y*Jz+z*Jy)*r2pp)*j3or3pp)+intAuU(3*(z*Jy+y*Jz)*j1orpp+2*k0^2*(5*y*z*rdotJpp-(y*Jz+z*Jy)*r2pp)*j3or3pp))");

      model.variable("post").set("qmxx", "30*(intAuL(x*rcxJxpp*j2or2pp)+intAuU(x*rcxJxpp*j2or2pp))");
      model.variable("post").set("qmyy", "30*(intAuL(y*rcxJypp*j2or2pp)+intAuU(y*rcxJypp*j2or2pp))");
      model.variable("post").set("qmzz", "30*(intAuL(z*rcxJzpp*j2or2pp)+intAuU(z*rcxJzpp*j2or2pp))");
      model.variable("post").set("qmxy", "15*(intAuL((x*rcxJypp+y*rcxJxpp)*j2or2pp)+intAuU((x*rcxJypp+y*rcxJxpp)*j2or2pp))");
      model.variable("post").set("qmxz", "15*(intAuL((x*rcxJzpp+z*rcxJxpp)*j2or2pp)+intAuU((x*rcxJzpp+z*rcxJxpp)*j2or2pp))");
      model.variable("post").set("qmyz", "15*(intAuL((y*rcxJzpp+z*rcxJypp)*j2or2pp)+intAuU((y*rcxJzpp+z*rcxJypp)*j2or2pp))");

      model.variable("post").set("C_ED", "k0^4/(6*pi*epsilon0_const^2*abs(E0)^2)*(abs(px)^2+abs(py)^2+abs(pz)^2)");
      model.variable("post").set("C_MD", "k0^4/(6*pi*epsilon0_const^2*abs(E0)^2)*(abs(mx/c_const)^2+abs(my/c_const)^2+abs(mz/c_const)^2)");
      model.variable("post").set("C_EQ", "k0^4/(720*pi*epsilon0_const^2*abs(E0)^2)*abs(k0)^2*(abs(qexx)^2+abs(qeyy)^2+abs(qezz)^2+2*abs(qexy)^2+2*abs(qexz)^2+2*abs(qeyz)^2)");
      model.variable("post").set("C_MQ", "k0^4/(720*pi*epsilon0_const^2*abs(E0)^2)*abs(k0/c_const)^2*(abs(qmxx)^2+abs(qmyy)^2+abs(qmzz)^2+2*abs(qmxy)^2+2*abs(qmxz)^2+2*abs(qmyz)^2)");

      // B32 convergence/closure observables.  EWFD's scattered-field
      // formulation exposes the solved relative electric field as relE.  The
      // total H field includes the analytic plane-wave background, so subtract
      // H_b=(0,E0/Zhost*exp(-i*k0*z),0) before forming the scattered Poynting
      // vector.  intBox is the closed six-face exterior box selection.
      model.variable("post").set("Zhost", "sqrt(mu0_const/(epsilon0_const*epsHost))");
      model.variable("post").set("I_inc", "0.5*abs(E0)^2/Zhost");
      model.variable("post").set("Hsbx", "ewfd.Hx");
      model.variable("post").set("Hsby", "ewfd.Hy-E0/Zhost*exp(-i*k0*z)");
      model.variable("post").set("Hsbz", "ewfd.Hz");
      model.variable("post").set("Sscax", "0.5*real(ewfd.relEy*conj(Hsbz)-ewfd.relEz*conj(Hsby))");
      model.variable("post").set("Sscay", "0.5*real(ewfd.relEz*conj(Hsbx)-ewfd.relEx*conj(Hsbz))");
      model.variable("post").set("Sscaz", "0.5*real(ewfd.relEx*conj(Hsby)-ewfd.relEy*conj(Hsbx))");
      model.variable("post").set("Stotx", "0.5*real(ewfd.Ey*conj(ewfd.Hz)-ewfd.Ez*conj(ewfd.Hy))");
      model.variable("post").set("Stoty", "0.5*real(ewfd.Ez*conj(ewfd.Hx)-ewfd.Ex*conj(ewfd.Hz))");
      model.variable("post").set("Stotz", "0.5*real(ewfd.Ex*conj(ewfd.Hy)-ewfd.Ey*conj(ewfd.Hx))");
      model.variable("post").set("P_sca_flux", "intBox(Sscax*nx+Sscay*ny+Sscaz*nz)");
      model.variable("post").set("P_total_out", "intBox(Stotx*nx+Stoty*ny+Stotz*nz)");
      model.variable("post").set("P_abs", "0.5*real(intAuL(Jx*conj(ewfd.Ex)+Jy*conj(ewfd.Ey)+Jz*conj(ewfd.Ez))+intAuU(Jx*conj(ewfd.Ex)+Jy*conj(ewfd.Ey)+Jz*conj(ewfd.Ez)))");
      model.variable("post").set("C_sca_flux", "P_sca_flux/I_inc");
      model.variable("post").set("C_multipole_sum", "C_ED+C_MD+C_EQ+C_MQ");
      model.variable("post").set("C_unresolved_signed", "C_sca_flux-C_multipole_sum");
      model.variable("post").set("C_unresolved_fraction", "abs(C_unresolved_signed)/abs(C_sca_flux)");
      model.variable("post").set("power_balance_fraction", "abs(P_total_out+P_abs)/(abs(P_total_out)+abs(P_abs))");

      stage = "solution_update";
      // These solution-dependent variables are defined after runAll().  COMSOL
      // 6.3 requires an explicit solution update before Results can resolve them.
      model.sol("sol1").updateSolution();

      stage = "result_nodes";
      // createAutoSequence already creates dset1; creating it again was the
      // B27 postprocessing failure.  Reuse and bind the existing dataset.
      model.result().dataset("dset1").set("solution", "sol1");
      model.result().table().create("tblMom", "Table");
      model.result().numerical().create("gevMom", "EvalGlobal");
      model.result().numerical("gevMom").set("data", "dset1");
      model.result().numerical("gevMom").set("expr", new String[]{
        "comp1.C_ED", "comp1.C_MD", "comp1.C_EQ", "comp1.C_MQ"
      });
      model.result().numerical("gevMom").set("table", "tblMom");
      model.result().numerical("gevMom").setResult();

      model.result().table().create("tblClosure", "Table");
      model.result().numerical().create("gevClosure", "EvalGlobal");
      model.result().numerical("gevClosure").set("data", "dset1");
      model.result().numerical("gevClosure").set("expr", new String[]{
        "comp1.P_sca_flux", "comp1.C_sca_flux", "comp1.C_multipole_sum",
        "comp1.C_unresolved_signed", "comp1.C_unresolved_fraction",
        "comp1.P_abs", "comp1.P_total_out", "comp1.power_balance_fraction"
      });
      model.result().numerical("gevClosure").set("table", "tblClosure");
      model.result().numerical("gevClosure").setResult();

      double[][] channels = model.result().numerical("gevMom").getReal();
      double cEd = resultValue(channels, 0);
      double cMd = resultValue(channels, 1);
      double cEq = resultValue(channels, 2);
      double cMq = resultValue(channels, 3);
      double[][] closure = model.result().numerical("gevClosure").getReal();
      double pSca = resultValue(closure, 0);
      double cSca = resultValue(closure, 1);
      double cMultipole = resultValue(closure, 2);
      double cUnresolved = resultValue(closure, 3);
      double unresolvedFraction = resultValue(closure, 4);
      double pAbs = resultValue(closure, 5);
      double pTotalOut = resultValue(closure, 6);
      double powerBalanceFraction = resultValue(closure, 7);
      System.out.println(
        "ALAEE2018_FIG3_MULTIPOLE_METRICS"
        + " case_id=" + currentCaseId
        + " x_alaee=" + currentX
        + " lambda_nm=" + (500.0/currentX)
        + " mesh_scale=" + currentMeshScale
        + " Lbox_nm=" + currentLboxNm
        + " C_ED_m2=" + cEd
        + " C_MD_m2=" + cMd
        + " C_EQ_m2=" + cEq
        + " C_MQ_m2=" + cMq
      );
      System.out.println(
        "ALAEE2018_FIG3_CLOSURE_METRICS"
        + " case_id=" + currentCaseId
        + " x_alaee=" + currentX
        + " mesh_scale=" + currentMeshScale
        + " Lbox_nm=" + currentLboxNm
        + " P_sca_flux_W=" + pSca
        + " C_sca_flux_m2=" + cSca
        + " C_multipole_sum_m2=" + cMultipole
        + " C_unresolved_signed_m2=" + cUnresolved
        + " unresolved_fraction=" + unresolvedFraction
        + " P_abs_W=" + pAbs
        + " P_total_out_W=" + pTotalOut
        + " power_balance_fraction=" + powerBalanceFraction
        + " omitted_order_role=aggregate_unresolved_not_l_resolved"
      );

      stage = "multipole_export";
      model.result().export().create("momCsv", "Table");
      model.result().export("momCsv").set("table", "tblMom");
      model.result().export("momCsv").set(
        "filename", "alaee2018_fig3_" + currentCaseId + "_multipoles.csv"
      );
      model.result().export("momCsv").run();

      stage = "closure_export";
      model.result().export().create("closureCsv", "Table");
      model.result().export("closureCsv").set("table", "tblClosure");
      model.result().export("closureCsv").set(
        "filename", "alaee2018_fig3_" + currentCaseId + "_closure.csv"
      );
      model.result().export("closureCsv").run();

      stage = "field_export";
      if (currentExportFields) {
        model.result().export().create("fieldEHJ", "Data");
        model.result().export("fieldEHJ").set("data", "dset1");
        model.result().export("fieldEHJ").set("expr", new String[]{
          "x", "y", "z", "ewfd.Ex", "ewfd.Ey", "ewfd.Ez",
          "ewfd.Hx", "ewfd.Hy", "ewfd.Hz", "comp1.Jx", "comp1.Jy", "comp1.Jz"
        });
        model.result().export("fieldEHJ").set(
          "filename", "alaee2018_fig3_" + currentCaseId + "_EHJ.csv"
        );
        model.result().export("fieldEHJ").run();
      }

      stage = "solution_payload_clear";
      // All live observables are now durable CSV/stdout artifacts.  Clear the
      // 1.88M-DOF native payload before COMSOL serializes the returned model;
      // the MPH retains geometry/physics/solver/result nodes and can rebuild.
      model.sol("sol1").clearSolutionData();
      System.out.println(
        "ALAEE2018_FIG3_POSTPROCESS_OK"
        + " case_id=" + currentCaseId
        + " field_export=" + currentExportFields
        + " solution_payload_cleared=true"
      );
      return true;
    } catch (Throwable failure) {
      System.out.println(
        "ALAEE2018_FIG3_POSTPROCESS_ERROR"
        + " stage=" + stage
        + " type=" + failure.getClass().getName()
        + " message=" + sanitizeMessage(failure.getMessage())
      );
      try {
        model.sol("sol1").clearSolutionData();
        System.out.println("ALAEE2018_FIG3_POSTPROCESS_FAILSAFE solution_payload_cleared=true");
      } catch (Throwable clearFailure) {
        System.out.println(
          "ALAEE2018_FIG3_POSTPROCESS_FAILSAFE"
          + " solution_payload_cleared=false"
          + " type=" + clearFailure.getClass().getName()
          + " message=" + sanitizeMessage(clearFailure.getMessage())
        );
      }
      return false;
    }
  }

  private static double resultValue(double[][] values, int index) {
    if (values.length == 0) return Double.NaN;
    if (values.length == 1 && values[0].length > index) return values[0][index];
    if (values.length > index && values[index].length > 0) return values[index][0];
    return Double.NaN;
  }

  private static String sanitizeMessage(String message) {
    if (message == null || message.length() == 0) return "none";
    return message.replace('\n', ' ').replace('\r', ' ').replace(' ', '_');
  }

  public static void main(String[] args) throws Exception {
    Model model = run();
    if (args.length > 0 && args[0].length() > 0) {
      model.save(args[0]);
    }
  }
}
