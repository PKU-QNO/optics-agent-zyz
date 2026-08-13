import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * Batch-safe COMSOL 6.3 engineering smoke for the Alaee 2018 Fig. 3 geometry.
 *
 * This is not a physical reproduction.  It deliberately reuses only the
 * repository-validated WaveOpticsProbe physics/study sequence:
 *
 *   ElectromagneticWavesFrequencyDomain + Frequency + createAutoSequence
 *
 * The gold material interpolation, background-field plane wave, scattering
 * boundary/PML, and field/current export must come from a COMSOL 6.3
 * GUI-exported Java/MPH template.  Those version-sensitive feature strings
 * are intentionally not guessed here.
 */
public class Alaee2018Fig3WaveOpticsSkeleton {
  public static Model run() throws Exception {
    Model model = ModelUtil.create("Model");
    model.modelNode().create("comp1");
    model.param().set("a", "250[nm]");
    model.param().set("t", "80[nm]");
    model.param().set("g", "120[nm]");
    model.param().set("lambda0", "800[nm]");
    model.param().set("freq0", "c_const/lambda0");
    model.param().set("Lxy", "2000[nm]");
    model.param().set("Lz", "1600[nm]");
    model.geom().create("geom1", 3);
    model.geom("geom1").lengthUnit("nm");
    model.geom("geom1").create("host", "Block");
    model.geom("geom1").feature("host").set("size", new String[]{"Lxy", "Lxy", "Lz"});
    model.geom("geom1").feature("host").set("pos", new String[]{"-Lxy/2", "-Lxy/2", "-Lz/2"});
    model.geom("geom1").create("diskLower", "Cylinder");
    model.geom("geom1").feature("diskLower").set("r", "a");
    model.geom("geom1").feature("diskLower").set("h", "t");
    model.geom("geom1").feature("diskLower").set("pos", new String[]{"0", "0", "-g/2-t"});
    model.geom("geom1").create("diskUpper", "Cylinder");
    model.geom("geom1").feature("diskUpper").set("r", "a");
    model.geom("geom1").feature("diskUpper").set("h", "t");
    model.geom("geom1").feature("diskUpper").set("pos", new String[]{"0", "0", "g/2"});
    model.geom("geom1").run();
    model.physics().create("emw", "ElectromagneticWavesFrequencyDomain", "geom1");
    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").automatic(false);
    model.mesh("mesh1").feature().create("size1", "Size");
    model.mesh("mesh1").feature("size1").set("hmax", "240[nm]");
    model.mesh("mesh1").feature("size1").set("hmin", "20[nm]");
    model.mesh("mesh1").feature().create("ftet1", "FreeTet");
    model.mesh("mesh1").run();
    model.study().create("std1");
    model.study("std1").create("freq", "Frequency");
    model.study("std1").feature("freq").set("plist", "freq0");
    model.sol().create("sol1");
    model.sol("sol1").study("std1");
    model.sol("sol1").createAutoSequence("std1");
    model.sol("sol1").runAll();
    int meshElements = model.mesh("mesh1").getNumElem();
    double[] solutionParameters = model.sol("sol1").getPVals();
    double solvedFrequency = solutionParameters.length > 0 ? solutionParameters[0] : Double.NaN;
    System.out.println("ALAEE2018_FIG3_WAVE_OPTICS_SMOKE_OK physics=ElectromagneticWavesFrequencyDomain study=Frequency mesh_elements=" + meshElements + " solution_parameter_hz=" + solvedFrequency);
    System.out.println("ALAEE2018_FIG3_SCIENCE_STATUS result_class=pipeline_smoke material_model=GUI_TEMPLATE_REQUIRED excitation=GUI_TEMPLATE_REQUIRED open_boundary_or_pml=GUI_TEMPLATE_REQUIRED field_export=GUI_TEMPLATE_REQUIRED neff=NOT_APPLICABLE_FREQUENCY_SCATTERING");
    return model;
  }

  public static void main(String[] args) throws Exception {
    Model model = run();
    if (args.length > 0) model.save(args[0]);
  }
}
