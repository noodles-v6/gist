import java.util.Random;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class UseCountDownLatch {

    public static void main (String[] args) {
        ExecutorService executor = Executors.newCachedThreadPool();
        CountDownLatch latch = new CountDownLatch(3);

        Worker w1 = new Worker(latch, "James");
        Worker w2 = new Worker(latch, "Eic");
        Worker w3 = new Worker(latch, "Lucy");

        Boss boss = new Boss(latch);

        executor.execute(w3);
        executor.execute(w2);
        executor.execute(w1);
        executor.execute(boss);

        executor.shutdown();
    }
}

class Worker implements Runnable {
    
    private CountDownLatch latch;
    private String name;

    public Worker(CountDownLatch latch, String name) {
        this.latch = latch;
        this.name  = name;
    }

    public void run() {
        this.doWork();
        try {
           TimeUnit.SECONDS.sleep(new Random().nextInt(20)); 
        } catch(InterruptedException e) {
        }
        System.out.println(this.name + " has done works");
        this.latch.countDown();
    }

    private void doWork() {
        System.out.println(this.name + " is working");
    }
}

class Boss implements Runnable {

    private CountDownLatch latch;
    
    public Boss(CountDownLatch latch) {
        this.latch = latch;
    }

    public void run() {
        System.out.println("Boss is waiting for all jobs be done");
        try {
           this.latch.await(); 
        } catch(InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("All jobs have done, so Boss will check them");
    }
}

