import java.io.FileInputStream;
import java.io.FileNotFoundException;


// 1. 直接 java SecurityTest 执行,看结果
// 2. 使用自定义权限执行: java -Djava.security.manager -Djava.security.policy=myapp.policy SecurityTest
public class SecurityTest {

    public static void main(String[] args)
        throws FileNotFoundException {

        System.out.println("SecurityManager: " +
                System.getSecurityManager());

        FileInputStream fin = new FileInputStream("test.txt");
        System.out.println("file opened ok");

        System.out.println(System.getProperty("file.encoding"));
    }
}
