import java.io.FileInputStream;
import java.io.FileNotFoundException;


// 1. 直接 java SecurityTest 执行,看结果
//    由于没有指定SecurityManager,所以所有权限都是开放的.
//    (System.getSecurityManager() is null. There is no SecurityManager so everything is allowed and we were able to successfully open a file and read the system property.)
// 2. 使用自定义权限执行: java -Djava.security.manager -Djava.security.policy=myapp.policy SecurityTest
//    这里指定了SecurityManager和policy文件了.
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
