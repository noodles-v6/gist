import java.util.Properties;

// http://www.jensign.com/JavaScience/www/javaproperties.html
public class props {
    static public void main(String args[]) {
        Properties props;
        props = System.getProperties();
        props.list(System.out);
    }
}
