import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.*;

public class MieScatteringTimeDomain2DMedium {
  public static void main(String[] args) throws Exception {
    runCase(
      "comsol-mie-td-medium",
      "MIE_SCATTERING_TD_MEDIUM_OK",
      8.0,
      0.80,
      1.75,
      0.18,
      3,
      "range(0,0.08,12)"
    ).saveIfRequested(args);
  }

  private static CaseResult runCase(
    String caseId,
    String marker,
    double domainSize,
    double radius,
    double refractiveIndex,
    double sourceWidth,
    int autoMeshSize,
    String tlist
  ) throws Exception {
    Model model = ModelUtil.create("Model");
    model.modelNode().create("comp1");
    model.param().set("L", domainSize + "[um]");
    model.param().set("r0", radius + "[um]");
    model.param().set("n_cyl", Double.toString(refractiveIndex));
    model.param().set("srcx", (-0.42 * domainSize) + "[um]");
    model.param().set("srcw", sourceWidth + "[um]");
    model.param().set("t0", "2.5");
    model.param().set("tau", "0.65");
    model.param().set("f0", "1.50");
    model.param().set("damp0", "0.22");
    model.param().set("abs_start", (0.38 * domainSize) + "[um]");

    model.geom().create("geom1", 2);
    model.geom("geom1").lengthUnit("um");
    model.geom("geom1").create("air", "Rectangle");
    model.geom("geom1").feature("air").set("size", new String[]{"L", "L"});
    model.geom("geom1").feature("air").set("pos", new String[]{"-L/2", "-L/2"});
    model.geom("geom1").run();

    model.physics().create("c", "CoefficientFormPDE", "geom1");
    model.physics("c").feature("cfeq1").set("ea", "if(x^2+y^2<r0^2,n_cyl^2,1)");
    model.physics("c").feature("cfeq1").set("da", "damp0*(if(abs(x)>abs_start,1,0)+if(abs(y)>abs_start,1,0))");
    model.physics("c").feature("cfeq1").set("c", "1");
    model.physics("c").feature("cfeq1").set("a", "0");
    model.physics("c").feature("cfeq1").set("f", "exp(-((x-srcx)/srcw)^2)*sin(2*pi*f0*t)*exp(-((t-t0)/tau)^2)");
    model.physics("c").feature("init1").set("u", "0");
    model.physics("c").create("dir1", "DirichletBoundary", 1);
    model.physics("c").feature("dir1").selection().all();
    model.physics("c").feature("dir1").set("r", "0");

    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").autoMeshSize(autoMeshSize);
    model.mesh("mesh1").run();

    model.study().create("std1");
    model.study("std1").create("time", "Transient");
    model.study("std1").feature("time").set("tlist", tlist);
    model.sol().create("sol1");
    model.sol("sol1").study("std1");
    model.sol("sol1").createAutoSequence("std1");
    model.sol("sol1").runAll();

    int meshElements = model.mesh("mesh1").getNumElem();
    writeMetrics(caseId, marker, domainSize, radius, refractiveIndex, sourceWidth, autoMeshSize, tlist, meshElements);
    System.out.println(marker + " mesh_elements=" + meshElements + " tlist=" + tlist);
    return new CaseResult(model);
  }

  private static void writeMetrics(
    String caseId,
    String marker,
    double domainSize,
    double radius,
    double refractiveIndex,
    double sourceWidth,
    int autoMeshSize,
    String tlist,
    int meshElements
  ) throws Exception {
    String metricsFile = System.getenv("OPTICS_COMSOL_METRICS_FILE");
    if (metricsFile != null && !metricsFile.isEmpty()) {
      writeMetricsFile(metricsFile, caseId, marker, domainSize, radius, refractiveIndex, sourceWidth, autoMeshSize, tlist, meshElements);
    }
    writeMetricsFile("mie_scattering_metrics.json", caseId, marker, domainSize, radius, refractiveIndex, sourceWidth, autoMeshSize, tlist, meshElements);
  }

  private static void writeMetricsFile(
    String metricsFile,
    String caseId,
    String marker,
    double domainSize,
    double radius,
    double refractiveIndex,
    double sourceWidth,
    int autoMeshSize,
    String tlist,
    int meshElements
  ) throws Exception {
    try (PrintWriter out = new PrintWriter(new FileWriter(metricsFile))) {
      out.println("{");
      out.println("  \"case_id\": \"" + caseId + "\",");
      out.println("  \"method\": \"2d_time_domain_scalar_wave_fem_fdtd_like\",");
      out.println("  \"status\": \"completed\",");
      out.println("  \"stdout_marker\": \"" + marker + "\",");
      out.println("  \"domain_size_um\": " + domainSize + ",");
      out.println("  \"scatterer_radius_um\": " + radius + ",");
      out.println("  \"scatterer_refractive_index\": " + refractiveIndex + ",");
      out.println("  \"source_width_um\": " + sourceWidth + ",");
      out.println("  \"auto_mesh_size\": " + autoMeshSize + ",");
      out.println("  \"time_steps\": \"" + tlist + "\",");
      out.println("  \"mesh_elements\": " + meshElements);
      out.println("}");
    }
  }

  private static class CaseResult {
    private final Model model;

    CaseResult(Model model) {
      this.model = model;
    }

    void saveIfRequested(String[] args) throws Exception {
      if (args.length > 0) model.save(args[0]);
    }
  }
}
