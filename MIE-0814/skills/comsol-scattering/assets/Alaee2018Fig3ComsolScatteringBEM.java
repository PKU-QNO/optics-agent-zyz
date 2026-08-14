import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.PrintWriter;
import java.util.Locale;

/**
 * Alaee 2018 Fig. 3: isolated 3-D RF boundary-element scattering builder.
 *
 * This file is intentionally independent of the established FEM builder.  It
 * contains only the two Au cylinders; the unbounded air region is represented
 * by COMSOL's infinite void.  Therefore no air box, SBC, or PML is present and
 * only the cylinder surfaces are triangulated.
 */
public class Alaee2018Fig3ComsolScatteringBEM {
  private static final String B41_CASE = "invalid";
  private static String currentCaseId = "invalid";
  private static double currentMeshScale = Double.NaN;

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
    if (B41_CASE.equals("mesh050")) {
      return runCase("b41_bem_mesh050_x360", 0.5);
    } else if (B41_CASE.equals("mesh030")) {
      return runCase("b41_bem_mesh030_x360", 0.3);
    } else if (B41_CASE.equals("mesh020")) {
      return runCase("b41_bem_mesh020_x360", 0.2);
    }
    throw new IllegalArgumentException("Unsupported B41 case: " + B41_CASE);
  }

  private static Model runCase(String caseId, double meshScale) throws Exception {
    currentCaseId = caseId;
    currentMeshScale = meshScale;
    Model model = ModelUtil.create("Alaee2018Fig3BEM");
    model.component().create("comp1");
    setParameters(model);
    defineJohnsonChristy(model);
    buildGeometry(model);
    buildMaterials(model);
    buildPhysics(model);
    buildSurfaceMesh(model);
    buildStudyAndSolve(model);
    exportFarFieldQuadrature(model);

    System.out.println(
      "B41_BEM_RUN_OK"
      + " case_id=" + currentCaseId
      + " physics_type=ElectromagneticWavesBoundaryElements"
      + " physics_tag=embe"
      + " x_alaee=0.36 lambda_nm=" + (500.0/0.36)
      + " mesh_scale=" + currentMeshScale
      + " surface_elements=" + model.component("comp1").mesh("mesh1").getNumElem()
      + " min_quality=" + model.component("comp1").mesh("mesh1").getMinQuality()
      + " sbc=false pml=false air_box=false"
      + " postprocess=surface_farfield_vsh_ready"
    );
    return model;
  }

  private static void setParameters(Model model) {
    model.param().set("a", "250[nm]");
    model.param().set("t", "80[nm]");
    model.param().set("g", "120[nm]");
    model.param().set("x_alaee", "0.36");
    model.param().set("lambda0", "2*a/x_alaee");
    model.param().set("lambda_nm", "lambda0/1[nm]");
    model.param().set("freq0", "c_const/lambda0");
    model.param().set("k0", "2*pi/lambda0");
    model.param().set("E0", "1[V/m]");
    model.param().set("epsHost", "1");
    model.param().set("Rfar", "100[um]");
    model.param().set("mesh_scale", Double.toString(currentMeshScale));
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
    model.component("comp1").variable().create("matvars");
    model.component("comp1").variable("matvars").set(
      "epsAu", "(nAu(lambda0)+i*kAu(lambda0))^2"
    );
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
    model.component("comp1").geom().create("geom1", 3);
    model.component("comp1").geom("geom1").lengthUnit("nm");
    model.component("comp1").geom("geom1").create("diskLower", "Cylinder");
    model.component("comp1").geom("geom1").feature("diskLower").set("r", "a");
    model.component("comp1").geom("geom1").feature("diskLower").set("h", "t");
    model.component("comp1").geom("geom1").feature("diskLower").set(
      "pos", new String[]{"0", "0", "-g/2-t"}
    );
    model.component("comp1").geom("geom1").feature("diskLower").set("selresultshow", "bnd");
    model.component("comp1").geom("geom1").create("diskUpper", "Cylinder");
    model.component("comp1").geom("geom1").feature("diskUpper").set("r", "a");
    model.component("comp1").geom("geom1").feature("diskUpper").set("h", "t");
    model.component("comp1").geom("geom1").feature("diskUpper").set(
      "pos", new String[]{"0", "0", "g/2"}
    );
    model.component("comp1").geom("geom1").feature("diskUpper").set("selresultshow", "bnd");
    model.component("comp1").geom("geom1").run();
    System.out.println(
      "B41_BEM_GEOMETRY_OK objects=2 air_box=false infinite_void=true"
    );
  }

  private static void buildMaterials(Model model) {
    model.component("comp1").material().create("matAir", "Common");
    model.component("comp1").material("matAir").selection().set(new int[]{});
    model.component("comp1").material("matAir").selection().allVoids();
    model.component("comp1").material("matAir").propertyGroup("def").set(
      "relpermittivity", "1"
    );
    model.component("comp1").material("matAir").propertyGroup("def").set(
      "relpermeability", "1"
    );
    model.component("comp1").material("matAir").propertyGroup("def").set(
      "electricconductivity", "0[S/m]"
    );
    // B41b PEC path: the two disk surfaces are PEC boundaries (BEM default),
    // so no dispersive gold material domain is defined here.  (matGoldLower/
    // matGoldUpper removed together with the Wave Equation, Electric nodes.)
  }

  private static void setGoldProperties(Model model, String tag) {
    model.component("comp1").material(tag).propertyGroup("def").set(
      "relpermittivity", new String[]{"epsAu", "0", "0", "0", "epsAu", "0", "0", "0", "epsAu"}
    );
    model.component("comp1").material(tag).propertyGroup("def").set(
      "relpermeability", new String[]{"1", "0", "0", "0", "1", "0", "0", "0", "1"}
    );
    model.component("comp1").material(tag).propertyGroup("def").set(
      "electricconductivity", "0[S/m]"
    );
  }

  private static void buildPhysics(Model model) {
    model.component("comp1").physics().create(
      "embe", "ElectromagneticWavesBoundaryElements", "geom1"
    );
    // B41: clear default domain selection before allVoids(), else FreeTri
    // cannot infer a BEM boundary selection (surface_elements=0 bug in r4).
    model.physics("embe").selection().set(new int[]{});
    model.component("comp1").physics("embe").selection().set(new int[]{});
    model.component("comp1").physics("embe").selection().allVoids();
    model.component("comp1").physics("embe").feature("wee1").set("DisplacementFieldModel", "RelativePermittivity");
    model.component("comp1").physics("embe").feature("wee1").set("epsilonr_mat", "userdef");
    model.component("comp1").physics("embe").feature("wee1").set("epsilonr", "epsHost");
    model.component("comp1").physics("embe").feature("wee1").set("mur_mat", "userdef");
    model.component("comp1").physics("embe").feature("wee1").set("mur", "1");
    model.component("comp1").physics("embe").feature("wee1").set("sigma_mat", "userdef");
    model.component("comp1").physics("embe").feature("wee1").set("sigma", "0[S/m]");

    // B41b-IBC path, step 1 (PEC approximation): the BEM scattered-field
    // formulation only supports constant-permittivity dielectric scatterers
    // and metallic PEC scatterers (official COMSOL 6.4 doc: "supports both
    // metallic PEC scatterers and dielectric scatterers"; a Wave Equation,
    // Electric node requires constant material params and cannot be
    // dispersive like Johnson-Christy gold).  Dispersive-metal material
    // domains (weeAuLower/weeAuUpper) leave the cylinder surfaces unselected
    // -> surface_elements=0.  Drop the dispersive Wave Equation, Electric
    // domains so the two cylinder surfaces fall back to the BEM default PEC
    // boundary, which IS meshed.  This is the Zs->0 limit of the intended
    // Impedance Boundary Condition; IBC (finite surface impedance) is added
    // next once the PEC path is confirmed.
    // (weeAuLower/weeAuUpper removed; the two disk surfaces become PEC.)

    model.component("comp1").physics("embe").prop("BackgroundField").set("SolveFor", "scatteredField");
    model.component("comp1").physics("embe").prop("BackgroundField").set(
      "Eb", new String[]{"E0*exp(-i*k0*z)", "0", "0"}
    );
    // B42 scheme A: ask the BEM interface to form COMSOL's native
    // Stratton-Chu far-field operator on every PEC surface adjacent to the
    // homogeneous infinite void.  FarName=Efar generates the direction
    // functions Efarx(dx,dy,dz), Efary(...), and Efarz(...).  COMSOL also
    // registers embe.Efarx/embe.Efary/embe.Efarz as variables, but the
    // callable direction functions themselves are intentionally unprefixed.
    model.component("comp1").physics("embe").create(
      "ffc1", "FarFieldCalculation", 2
    );
    model.component("comp1").physics("embe").feature("ffc1")
      .selection().geom("geom1", 2);
    model.component("comp1").physics("embe").feature("ffc1")
      .selection().all();
    model.component("comp1").physics("embe").feature("ffc1")
      .set("FarName", "Efar");
    model.component("comp1").physics("embe").feature("ffc1")
      .set("FarFieldBoundarySide", "FarFieldBoundaryOutside");
    System.out.println(
      "B41_BEM_PHYSICS_OK physics_type=ElectromagneticWavesBoundaryElements"
      + " physics_tag=embe formulation=scatteredField"
      + " incident=E0_exp_minus_i_k0_z polarization=x propagation=plus_z"
      + " finite_wave_equations=2 far_field_calculation=true"
      + " far_field_feature=ffc1 far_field_name=Efar"
      + " far_field_selection=all_pec_surfaces boundary_side=outside"
      + " far_field_path=Efar_direction_functions"
    );
  }

  private static void buildSurfaceMesh(Model model) {
    model.component("comp1").mesh().create("mesh1", "geom1");
    model.component("comp1").mesh("mesh1").feature().create("size1", "Size");
    model.component("comp1").mesh("mesh1").feature("size1").set(
      "hmax", Double.toString(35.0*currentMeshScale) + "[nm]"
    );
    model.component("comp1").mesh("mesh1").feature("size1").set(
      "hmin", Double.toString(8.0*currentMeshScale) + "[nm]"
    );
    model.component("comp1").mesh("mesh1").feature().create("ftri1", "FreeTri");
    // In a 3-D model FreeTri operates on boundaries (GEOMDIM=2), and its
    // default selection is empty. Calling all() without first fixing the
    // selection dimension left the two material-domain cylinders unmeshed
    // (B41 r3: surface_elements=0). The official COMSOL 6.3
    // rcs_sphere_bem.mph stores ftri1 as dim=2/hDim=2; make that contract
    // explicit here so all exterior faces of both Au domains are selected.
    model.component("comp1").mesh("mesh1").feature("ftri1")
      .selection().geom("geom1", 2);
    model.component("comp1").mesh("mesh1").feature("ftri1").selection().all();
    model.component("comp1").mesh("mesh1").run();
    System.out.println(
      "B41_BEM_SURFACE_MESH_OK"
      + " case_id=" + currentCaseId
      + " mesh_type=FreeTri selection_dim=2 selection_scope=all_boundaries"
      + " mesh_scale=" + currentMeshScale
      + " hmax_nm=" + (35.0*currentMeshScale)
      + " hmin_nm=" + (8.0*currentMeshScale)
      + " surface_elements=" + model.component("comp1").mesh("mesh1").getNumElem()
      + " min_quality=" + model.component("comp1").mesh("mesh1").getMinQuality()
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
    System.out.println("B41_BEM_SOLVE_OK case_id=" + currentCaseId);
  }

  private static void exportFarFieldQuadrature(Model model) throws Exception {
    final int nMu = 16;
    final int nPhi = 32;
    double[][] gauss = gaussLegendre(nMu);
    model.result().dataset("dset1").set("solution", "sol1");
    model.result().numerical().create("gevFar", "EvalGlobal");
    model.result().numerical("gevFar").set("data", "dset1");

    String filename = "alaee2018_fig3_" + currentCaseId + "_farfield.csv";
    java.io.PrintWriter out = new java.io.PrintWriter(filename, "UTF-8");
    out.println("mu,phi_rad,weight,dx,dy,dz,Efarx_re,Efarx_im,Efary_re,Efary_im,Efarz_re,Efarz_im");
    double weightedNorm2 = 0.0;
    try {
      for (int i = 0; i < nMu; i++) {
        double mu = gauss[0][i];
        double wMu = gauss[1][i];
        double sinTheta = Math.sqrt(Math.max(0.0, 1.0-mu*mu));
        for (int j = 0; j < nPhi; j++) {
          double phi = 2.0*Math.PI*j/nPhi;
          double dx = sinTheta*Math.cos(phi);
          double dy = sinTheta*Math.sin(phi);
          double dz = mu;
          String sx = String.format(Locale.US, "%.17g", dx);
          String sy = String.format(Locale.US, "%.17g", dy);
          String sz = String.format(Locale.US, "%.17g", dz);
          model.result().numerical("gevFar").set("expr", new String[]{
            "Efarx(" + sx + "," + sy + "," + sz + ")/E0",
            "Efary(" + sx + "," + sy + "," + sz + ")/E0",
            "Efarz(" + sx + "," + sy + "," + sz + ")/E0"
          });
          double[][] real = model.result().numerical("gevFar").getReal();
          double[][] imag = model.result().numerical("gevFar").getImag();
          double rx = resultValue(real, 0);
          double ry = resultValue(real, 1);
          double rz = resultValue(real, 2);
          double ix = resultValue(imag, 0);
          double iy = resultValue(imag, 1);
          double iz = resultValue(imag, 2);
          double weight = wMu*2.0*Math.PI/nPhi;
          weightedNorm2 += weight*(rx*rx+ix*ix+ry*ry+iy*iy+rz*rz+iz*iz);
          out.printf(
            Locale.US,
            "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g%n",
            mu, phi, weight, dx, dy, dz, rx, ix, ry, iy, rz, iz
          );
        }
      }
    } finally {
      out.close();
    }
    System.out.println(
      "B41_BEM_FARFIELD_EXPORT_OK"
      + " case_id=" + currentCaseId
      + " n_mu=" + nMu + " n_phi=" + nPhi
      + " samples=" + (nMu*nPhi)
      + " far_field_feature=ffc1 far_field_name=Efar"
      + " evaluation=Efar_direction_functions_over_E0"
      + " quadrature_weight_sum=" + (4.0*Math.PI)
      + " C_sca_farfield_m2=" + weightedNorm2
      + " filename=" + filename
    );
  }

private static double resultValue(double[][] values, int index) {
    if (values == null || values.length == 0) return 0.0;
    if (values.length == 1 && values[0].length > index) return values[0][index];
    if (values.length > index && values[index].length > 0) return values[index][0];
    throw new IllegalStateException("Unexpected numerical result shape");
  }

  /** Golub-Welsch-free Newton construction of Gauss-Legendre nodes/weights. */
  private static double[][] gaussLegendre(int n) {
    double[] x = new double[n];
    double[] w = new double[n];
    int m = (n+1)/2;
    for (int i = 0; i < m; i++) {
      double z = Math.cos(Math.PI*(i+0.75)/(n+0.5));
      double pp = 0.0;
      for (int iter = 0; iter < 100; iter++) {
        double p1 = 1.0;
        double p2 = 0.0;
        for (int j = 1; j <= n; j++) {
          double p3 = p2;
          p2 = p1;
          p1 = ((2.0*j-1.0)*z*p2-(j-1.0)*p3)/j;
        }
        pp = n*(z*p1-p2)/(z*z-1.0);
        double next = z-p1/pp;
        if (Math.abs(next-z) < 1e-15) {
          z = next;
          break;
        }
        z = next;
      }
      x[i] = -z;
      x[n-1-i] = z;
      w[i] = 2.0/((1.0-z*z)*pp*pp);
      w[n-1-i] = w[i];
    }
    return new double[][]{x, w};
  }

  public static void main(String[] args) throws Exception {
    Model model = run();
    if (args.length > 0 && args[0].length() > 0) model.save(args[0]);
  }
}
