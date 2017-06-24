package verification;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Scanner;

/**
 * Construct the nodes for searching for a verification tree.
 *
 * @author Michael Albert
 */
public class Nodes {

    Node[] nodes;
    int root;

    public Nodes(Node[] nodes) {
        this.nodes = nodes;
        updateAll();
    }

    public Nodes(String fileName) throws FileNotFoundException, IOException {
        BufferedReader in = new BufferedReader(new FileReader(fileName));
        nodes = new Node[Integer.parseInt(in.readLine()) + 1];
        root = Integer.parseInt(in.readLine());
        for (int i = 0; i < nodes.length; i++) {
            nodes[i] = new Node();
        }
        while (true) {
            String line = in.readLine();
            if (line == null) {
                break;
            }
            Scanner rule = new Scanner(line);
            int i = rule.nextInt();
            ArrayList<Node> v = new ArrayList<>();
            while (rule.hasNextInt()) {
                v.add(nodes[rule.nextInt()]);
            }
            nodes[i].addWitness(v);
        }

        updateAll();

    }

    private void updateAll() {
        while (true) {
            boolean changed = false;
            for (Node n : nodes) {
                changed |= n.update();
            }
            if (!changed) {
                break;
            }
        }
    }
    
    public static void main(String[] args) throws IOException {
        Nodes n = new Nodes(args[0]);
        long start = System.currentTimeMillis();
        TreesStrategy t = new TreesStrategy(n.nodes);
        System.out.println("Time: " + (System.currentTimeMillis() - start));
        
    }

}
