import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.*;

public class CorePdeEigenmode {
  public static void main(String[] args) throws Exception {
    Model model = ModelUtil.create("Model");
    model.modelNode().create("comp1");
    model.geom().create("geom1", 2);
    model.geom("geom1").create("pol1", "Polygon");
    model.geom("geom1").feature("pol1").set("source", "table");
    model.geom("geom1").feature("pol1").set("table", new String[][]{
      {"-1","-1"},{"0","-1"},{"0","0"},{"1","0"},{"1","1"},{"-1","1"}
    });
    model.geom("geom1").run();
    model.physics().create("c", "CoefficientFormPDE", "geom1");
    model.physics("c").feature("cfeq1").set("c", "1");
    model.physics("c").feature("cfeq1").set("a", "0");
    model.physics("c").feature("cfeq1").set("f", "0");
    model.physics("c").feature("cfeq1").set("da", "1");
    model.physics("c").create("dir1", "DirichletBoundary", 1);
    model.physics("c").feature("dir1").selection().all();
    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").autoMeshSize(3);
    model.mesh("mesh1").run();
    model.study().create("std1");
    model.study("std1").create("eig", "Eigenvalue");
    model.study("std1").feature("eig").set("neigs", 6);
    model.sol().create("sol1");
    model.sol("sol1").study("std1");
    model.sol("sol1").createAutoSequence("std1");
    model.sol("sol1").runAll();
    double[] ev = model.sol("sol1").getPVals();
    StringBuilder values = new StringBuilder();
    for (double e : ev) values.append(e).append(" ");
    writeMetrics("core-pde-eigenmode", "core_pde", "completed", values.toString().trim());
    if (args.length > 0) model.save(args[0]);
    System.out.println("CORE_PDE_EIGENMODE_OK " + values.toString().trim());
  }

  private static void writeMetrics(String caseId, String capability, String status, String values) throws Exception {
    String metricsFile = System.getenv("OPTICS_COMSOL_METRICS_FILE");
    if (metricsFile == null || metricsFile.isEmpty()) return;
    try (PrintWriter out = new PrintWriter(new FileWriter(metricsFile))) {
      out.println("{");
      out.println("  \"case_id\": \"" + caseId + "\",");
      out.println("  \"capability\": \"" + capability + "\",");
      out.println("  \"status\": \"" + status + "\",");
      out.println("  \"eigenvalues\": \"" + values + "\",");
      out.println("  \"lambda1_reference\": 9.6397238");
      out.println("}");
    }
  }
}
