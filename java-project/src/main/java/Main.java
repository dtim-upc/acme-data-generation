import org.apache.commons.cli.*;
import airbase.DataGen;

public class Main {
    public static void main(String[] args) throws Exception {

        // parse arguments
        // https://stackoverflow.com/questions/367706/how-do-i-parse-command-line-arguments-in-java
        Options options = new Options();

        Option genArg = new Option("g", "generate", true, "Number of instances to generate");
        genArg.setRequired(false);
        options.addOption(genArg);

        Option outputArg = new Option("out", "outFolderPath", true, "path to output folder");
        outputArg.setRequired(false);
        options.addOption(outputArg);

        CommandLineParser parser = new DefaultParser();
        HelpFormatter formatter = new HelpFormatter();
        CommandLine cmd = null;

        try {
            cmd = parser.parse(options, args);
        } catch (ParseException e) {
            System.out.println(e.getMessage());
            formatter.printHelp("DataGen", options, true);
            System.exit(1);
        }

        // dispatch arguments
        Integer genNum = Integer.valueOf(cmd.getOptionValue("generate", "1000"));
        String outputFilePath = cmd.getOptionValue("outFolderPath");

        //run generator
        DataGen dg = new DataGen();
        dg.generate();
    }
}
