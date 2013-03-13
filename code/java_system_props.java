 import java.util.Properties;

 public class props {
     static public void main(String args[]) {
         Properties props;
         props = System.getProperties();
         props.list(System.out);
     }
 }
