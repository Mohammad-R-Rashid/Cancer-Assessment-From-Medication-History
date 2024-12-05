import weka.core.Instances;
import weka.core.converters.ConverterUtils.DataSource;
import weka.classifiers.functions.LinearRegression;

public class RegressionModel {
    public static void main(String[] args) {
        try {
            // Load the dataset
            DataSource dataSource = new DataSource("path/to/your/dataset.arff"); // Replace with your dataset path
            Instances data = dataSource.getDataSet();

            // Set the index of the dependent variable (class attribute)
            // Assumes the dependent variable is the last column
            if (data.classIndex() == -1) {
                data.setClassIndex(data.numAttributes() - 1);
            }

            // Build the Linear Regression model
            LinearRegression model = new LinearRegression();
            model.buildClassifier(data);

            // Print the regression model
            System.out.println("Regression Model: ");
            System.out.println(model);

            // Make a prediction on a new instance
            double[] newValues = {5.1, 3.5, 1.4}; // Replace with your own feature values
            Instances newData = new Instances(data, 0);
            newData.add(data.instance(0).copy(newValues));
            newData.setClassIndex(newData.numAttributes() - 1);

            double predictedValue = model.classifyInstance(newData.instance(0));
            System.out.println("Predicted Value: " + predictedValue);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
