import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import weka.core.Instances;
import weka.core.tokenizers.WordTokenizer;

/** Checks ARFF parsing and the exact WEKA tokenizer proposed for Member 2. */
public class ValidateData {
    public static void main(String[] args) throws Exception {
        for (String language : List.of("en", "hi")) {
            Path path = Path.of("data", "processed", language + "_reviews.arff");
            try (Reader reader = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
                Instances data = new Instances(reader);
                data.setClassIndex(data.numAttributes() - 1);
                require(data.numAttributes() == 2, "Unexpected metadata in ARFF");
                require(data.relationName().equals("cinemood_" + language), "Unexpected relation name");
                require(data.attribute(0).name().equals("review"), "Unexpected text attribute name");
                require(data.attribute(0).isString(), "Review must be string");
                require(data.classAttribute().name().equals("sentiment"), "Unexpected class attribute name");
                require(data.classAttribute().isNominal() && data.numClasses() == 2, "Class must be binary nominal");
                require(data.classAttribute().value(0).equals("negative")
                        && data.classAttribute().value(1).equals("positive"), "Unexpected class values or order");
                int[] counts = new int[2];
                for (int i = 0; i < data.numInstances(); i++) {
                    require(!data.instance(i).hasMissingValue(), "Missing field");
                    counts[(int) data.instance(i).classValue()]++;
                    String text = data.instance(i).stringValue(0);
                    require(!text.isBlank(), "Empty review");
                    require(tokens(text).equals(Arrays.asList(text.split(" "))), "Tokenizer changed prepared text");
                }
                require(counts[0] >= 10 && counts[1] >= 10, "Each class needs at least 10 records");
                System.out.printf("%s: %d rows; negative=%d, positive=%d; ARFF and all token boundaries passed%n",
                                  language, data.numInstances(), counts[0], counts[1]);
            }
        }
        require(tokens("यह फिल्म अच्छी नहीं है").contains("नहीं"), "Hindi negation lost");
        require(tokens("I don't like this film").contains("don't"), "English contraction split");
        require(tokens("अच्छी कहानी शानदार अभिनय").equals(List.of("अच्छी", "कहानी", "शानदार", "अभिनय")),
                "Devanagari marks split");
        System.out.println("WEKA whitespace WordTokenizer: Hindi combining marks and English/Hindi negation passed");
        System.out.println("Validation only: no model training or accuracy evaluation performed");
    }

    private static List<String> tokens(String text) {
        WordTokenizer tokenizer = new WordTokenizer();
        tokenizer.setDelimiters(" \r\n\t");
        tokenizer.tokenize(text);
        List<String> result = new ArrayList<>();
        while (tokenizer.hasMoreElements()) result.add(tokenizer.nextElement());
        return result;
    }

    private static void require(boolean condition, String message) {
        if (!condition) throw new IllegalStateException(message);
    }
}
