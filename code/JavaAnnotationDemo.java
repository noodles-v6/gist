import java.lang.reflect.*;
import java.lang.annotation.*;

@MyClassAnnotation(uri="JavaAnnotationDemo", desc="the class name")
public class JavaAnnotationDemo {

    @MyFieldAnnotation(uri="JavaAnnotationDemo#id", desc="the class field")
    public String id;

    @MyConstructorAnnotation(uri="JavaAnnotationDemo#JavaAnnotationDemo", desc="the desc")
    public JavaAnnotationDemo() {
    }

    @MyMethodAnnotation(uri="JavaAnnotationDemo#setId", desc="the class method")
    public void set(String id) {
        this.id = id;
    }

    public static void main (String[] args) {
        JavaAnnotationDemo demo = new JavaAnnotationDemo();
       
        MyClassAnnotation oMyAnnotation = JavaAnnotationDemo.class
            .getAnnotation(MyClassAnnotation.class);
        System.out.println("Class's uri:" + oMyAnnotation.uri());

        Constructor oConstructor = demo.getClass().getConstructors()[0];
        MyConstructorAnnotation oConstrAnn = (MyConstructorAnnotation) oConstructor
            .getAnnotation(MyConstructorAnnotation.class);
        System.out.println("Constructor's uri: " + oConstrAnn.uri());
    }
}

@Retention(RetentionPolicy.RUNTIME)   
@Target(ElementType.TYPE) 
@interface MyClassAnnotation
{
    String uri();
    String desc();
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.CONSTRUCTOR)
@interface MyConstructorAnnotation
{
    String uri();
    String desc();
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface MyMethodAnnotation
{
    String uri();
    String desc();
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface MyFieldAnnotation
{
    String uri();
    String desc();
}
