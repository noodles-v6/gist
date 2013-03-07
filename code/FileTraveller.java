import java.io.File;
import java.io.FilenameFilter;

// 带过滤器的目录结构工具
public class FileTraveller {

    private File file;
    private int deep = 0;
    
    public FileTraveller(String dirName) {
        this.file = new File(dirName);
    }
    
    public FileTraveller(File dir, int deep) {
        this.file = dir;
        this.deep = deep;
    }
    
    public void travel(FilenameFilter filter) {
        if (this.file.isDirectory()) {
            this.print();
            for (File f : this.file.listFiles(filter)) {
                new FileTraveller(f, this.deep + 1).travel(filter);
            }
        }
        else {
            this.print();
        }
    }
    
    private void print() {
        int d = deep;
        while (d-- > 0) {
            System.out.print("  |- ");
        }
            
        System.out.println(this.file.getName());
    }
    

    // test
    public static void main(String[] args) {
        
        String baseDirName = ".";
        FileTraveller traveller = new FileTraveller(baseDirName);
        traveller.travel(new FilenameFilter() {
            @Override
            public boolean accept(File dir, String name) {
                if (name.startsWith(".")) {
                    return false;
                }
                return true;
            }
        });
        
    }
    
}

