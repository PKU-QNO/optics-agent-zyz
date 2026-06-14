import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.*;

public class WaveOpticsProbe {
  public static void main(String[] args) throws Exception {
    Model model = ModelUtil.create("Model");
    model.modelNode().create("comp1");
    model.param().set("freq0", "3e14[Hz]");
    model.geom().create("geom1", 2);
    model.geom("geom1").lengthUnit("um");
    model.geom("geom1").create("r1", "Rectangle");
    model.geom("geom1").feature("r1").set("size", new String[]{"1", "1"});
    model.geom("geom1").run();
    String selected = createFirstAvailablePhysics(model, "emw", new String[]{
      "ElectromagneticWavesFrequencyDomain",
      "ElectromagneticWaves"
    });
    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").autoMeshSize(5);
    model.mesh("mesh1").run();
    model.study().create("std1");
    model.study("std1").create("freq", "Frequency");
    model.study("std1").feature("freq").set("plist", "freq0");
    model.sol().create("sol1");
    model.sol("sol1").study("std1");
    model.sol("sol1").createAutoSequence("std1");
    model.sol("sol1").runAll();
    writeMetrics("wave-optics-probe", "wave_optics_or_rf", "completed", selected);
    if (args.length > 0) model.save(args[0]);
    System.out.println("WAVE_OPTICS_PROBE_OK physics=" + selected);
  }

  private static String createFirstAvailablePhysics(Model model, String tag, String[] candidates) {
    StringBuilder errors = new StringBuilder();
    for (String candidate : candidates) {
      try {
        model.physics().create(tag, candidate, "geom1");
        return candidate;
      } catch (Exception ex) {
        errors.append(candidate).append(": ").append(ex.getMessage()).append("; ");
      }
    }
    throw new RuntimeException("No Wave Optics/RF candidate interface could be created: " + errors.toString());
  }

  private static void writeMetrics(String caseId, String capability, String status, String selectedPhysics) throws Exception {
    String metricsFile = System.getenv("OPTICS_COMSOL_METRICS_FILE");
    if (metricsFile == null || metricsFile.isEmpty()) return;
    try (PrintWriter out = new PrintWriter(new FileWriter(metricsFile))) {
      out.println("{");
      out.println("  \"case_id\": \"" + caseId + "\",");
      out.println("  \"capability\": \"" + capability + "\",");
      out.println("  \"status\": \"" + status + "\",");
      out.println("  \"selected_physics\": \"" + selectedPhysics + "\"");
      out.println("}");
    }
  }
}
