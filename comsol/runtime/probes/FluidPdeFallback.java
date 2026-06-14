import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.*;

public class FluidPdeFallback {
  public static void main(String[] args) throws Exception {
    Model model = ModelUtil.create("Model");
    model.modelNode().create("comp1");
    model.geom().create("geom1", 2);
    model.geom("geom1").lengthUnit("mm");
    model.geom("geom1").create("r1", "Rectangle");
    model.geom("geom1").feature("r1").set("size", new String[]{"4", "1"});
    model.geom("geom1").run();
    model.physics().create("c", "CoefficientFormPDE", "geom1");
    model.physics("c").feature("cfeq1").set("c", "1");
    model.physics("c").feature("cfeq1").set("a", "0");
    model.physics("c").feature("cfeq1").set("f", "1");
    model.physics("c").create("dir1", "DirichletBoundary", 1);
    model.physics("c").feature("dir1").selection().all();
    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").autoMeshSize(4);
    model.mesh("mesh1").run();
    model.study().create("std1");
    model.study("std1").create("stat", "Stationary");
    model.sol().create("sol1");
    model.sol("sol1").study("std1");
    model.sol("sol1").createAutoSequence("std1");
    model.sol("sol1").runAll();
    writeMetrics("fluid-pde-fallback", "fluid_like_core_pde_fallback", "completed", model.mesh("mesh1").getNumElem());
    if (args.length > 0) model.save(args[0]);
    System.out.println("FLUID_PDE_FALLBACK_OK mesh_elements=" + model.mesh("mesh1").getNumElem());
  }

  private static void writeMetrics(String caseId, String capability, String status, int meshElements) throws Exception {
    String metricsFile = System.getenv("OPTICS_COMSOL_METRICS_FILE");
    if (metricsFile == null || metricsFile.isEmpty()) return;
    try (PrintWriter out = new PrintWriter(new FileWriter(metricsFile))) {
      out.println("{");
      out.println("  \"case_id\": \"" + caseId + "\",");
      out.println("  \"capability\": \"" + capability + "\",");
      out.println("  \"status\": \"" + status + "\",");
      out.println("  \"mesh_elements\": " + meshElements);
      out.println("}");
    }
  }
}
