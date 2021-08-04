package analytics;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicSessionCredentials;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.event.S3EventNotification;
import com.amazonaws.services.s3.event.S3EventNotification.S3EventNotificationRecord;
import com.amazonaws.services.s3.model.PutObjectRequest;
import com.amazonaws.services.s3.model.PutObjectResult;
import com.amazonaws.services.s3.model.S3Object;
import com.kennycason.kumo.CollisionMode;
import com.kennycason.kumo.WordCloud;
import com.kennycason.kumo.WordFrequency;
import com.kennycason.kumo.bg.CircleBackground;
import com.kennycason.kumo.font.KumoFont;
import com.kennycason.kumo.font.scale.SqrtFontScalar;
import com.kennycason.kumo.nlp.FrequencyAnalyzer;
import com.kennycason.kumo.nlp.tokenizers.ChineseWordTokenizer;
import com.kennycason.kumo.palette.ColorPalette;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;
import software.amazon.awssdk.regions.Region;

public class Main implements RequestHandler<S3EventNotification, String> {
    public Main() {
    }

    public String handleRequest(S3EventNotification s3EventNotification, Context context) {
        List<String> words = new ArrayList();
        Region region = Region.US_EAST_1;
        BasicSessionCredentials credentials = new BasicSessionCredentials("ASIARXYWXFBEUUUBJM7L", "B0OgJDQSNmv2tjctmPSKrs2VMxg5pOLeyalQC88+", "FwoGZXIvYXdzELX//////////wEaDM0oW8Mv4vpIcVDWXyK/AfHAAQYtloxdERtbXLeVKOlOgmuQdERlZv8afBAn27vcP0whgVHB5o8d/PXM7CsRE7t3DXv1OUYBOuk52OW+mR1aHtgBt3yo7PrIWRDZ+MOb0y5vaqC/zkKoKzGW+a5TFBQb6sADEn9spR++55aPLVqHUw4bmWyuo3AvmKzz91rZEej35v2Kb6p9LZ3a1p/21M89VDEVi0SgbNRxg5vrR9A1jTBi29k+nTilJaW0cpqwWLrHTZAfRWhb2qRh8d29KP6A2YcGMi2KzRpxxyADm57+1GRUYQGhA55RwD6llaB7XylX3GdxOFrRE4DUoNHtRHqfm9c=");
        AmazonS3 s3Client = (AmazonS3)((AmazonS3ClientBuilder)((AmazonS3ClientBuilder)AmazonS3ClientBuilder.standard().withRegion(String.valueOf(region))).withCredentials(new AWSStaticCredentialsProvider(credentials))).build();
        S3EventNotificationRecord s3EventNotificationRecord = (S3EventNotificationRecord)s3EventNotification.getRecords().get(0);
        String bucketName = s3EventNotificationRecord.getS3().getBucket().getName();
        String objectName = s3EventNotificationRecord.getS3().getObject().getKey();
        S3Object s3Object = s3Client.getObject(bucketName, objectName);
        InputStream inputStream = s3Object.getObjectContent();
        BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream));
        System.out.println("Generating words ...");
        String[] targetObject = objectName.split("\\.");

        try {
            String st;
            while((st = bufferedReader.readLine()) != null) {
                st = st.trim();
                st.replace("'", "");
                st.replace("\"", "");
                st.replace("\\.", "");
                st.replace(",", "");
                words.add(st);
                System.out.println(st);
            }

            System.out.println("Calling the word web function ...");
            System.out.println("Filename: " + targetObject[0] + ".png");
            File newFile = new File("/tmp/" + targetObject[0] + ".png");
            if (!newFile.createNewFile()) {
                System.out.println("Over writing file ...");
            }

            this.getWordCloud(words, targetObject[0]);
            new PutObjectResult();
            s3Client.putObject(new PutObjectRequest("skim-meeting-output1", targetObject[0] + ".png", newFile));
        } catch (Exception var17) {
            System.out.println(var17);
        }

        return "successful";
    }

    public void getWordCloud(List<String> words, String targetObject) throws IOException {
        FrequencyAnalyzer frequencyAnalyzer = new FrequencyAnalyzer();
        frequencyAnalyzer.setWordFrequenciesToReturn(600);
        frequencyAnalyzer.setMinWordLength(2);
        frequencyAnalyzer.setWordTokenizer(new ChineseWordTokenizer());
        List<WordFrequency> wordFrequencyList = frequencyAnalyzer.load(words);
        Dimension dimension = new Dimension(500, 500);
        WordCloud wordCloud = new WordCloud(dimension, CollisionMode.PIXEL_PERFECT);
        Font font = new Font("STSong-Light", 2, 18);
        wordCloud.setKumoFont(new KumoFont(font));
        wordCloud.setPadding(2);
        wordCloud.setColorPalette(new ColorPalette(new Color[]{new Color(15538497), new Color(15885602), new Color(8672568), new Color(9067801), new Color(8353058), new Color(6060585), new Color(1938751), new Color(32101), new Color(6668948)}));
        wordCloud.setBackground(new CircleBackground(200));
        wordCloud.setFontScalar(new SqrtFontScalar(10, 40));
        wordCloud.setBackgroundColor(new Color(255, 255, 255));
        wordCloud.build(wordFrequencyList);
        OutputStream output = new ByteArrayOutputStream();
        wordCloud.writeToStream("png", output);
        byte[] outputByte = ((ByteArrayOutputStream)output).toByteArray();
        OutputStream os = new FileOutputStream("/tmp/" + targetObject + ".png");
        os.write(outputByte);
        System.out.println("Word web file generated successfully ...");
        os.close();
    }
}
