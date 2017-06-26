package bfs_tilescope;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.io.*;

/**
 * Use the tilescope on a data file. Data format should be:
 * <maximum index>
 * <root node> -- though this is now superfluous
 * <list of productions one per line>
 *
 * where a production is just the index of the source followed by the 
 * index of the children.
 *
 * @author Michael Albert
 */
public class App {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws FileNotFoundException, IOException {
        BufferedReader in = new BufferedReader(new FileReader(args[0]));
        System.out.println("Input file: " + args[0]);
        Node[] nodes = new Node[Integer.parseInt(in.readLine()) + 1];
        int root = Integer.parseInt(in.readLine());
        System.out.println("Root node: " + root);
        System.out.println();
        for (int i = 0; i < nodes.length; i++) {
            nodes[i] = new Node();
        }
        Universe u = new Universe(nodes);
        while (true) {
            String line = in.readLine();
            if (line == null) {
                break;
            }
            u.addProduction(line);
        }
        long start = System.currentTimeMillis();
        HashMap<Integer, Collection<Node>> proof = u.proof();
        System.out.println("Time taken " + (System.currentTimeMillis()-start) + " ms.");
        if (proof.containsKey(root)) {
            System.out.println("Proof found for root which begins:");
            System.out.print(root + " -> ");
            for(Node n : proof.get(root)) {
                System.out.print(n.id + " ");
            }
            System.out.println();
        } else {
            System.out.println("No proof found for root");
        }
        System.out.println();
        System.out.println("All proofs:");
        
        for(int i : proof.keySet()) {
            System.out.print(i + " -> ");
            for(Node n : proof.get(i)) {
                System.out.print(n.id + " ");
            }
            System.out.println();
        }
    }
    
}

